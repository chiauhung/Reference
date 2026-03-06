import logging
import re
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import ContextManager

import click
from git.repo.base import Repo
from semantic_release.changelog import ReleaseHistory, environment
from semantic_release.changelog.context import make_changelog_context
from semantic_release.cli.commands.version import apply_version_to_source_files
from semantic_release.cli.common import (
    render_default_changelog_file,
    render_release_notes,
)
from semantic_release.cli.config import (
    GlobalCommandLineOptions,
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.util import load_raw_config_file
from semantic_release.commit_parser import (
    AngularCommitParser,
    AngularParserOptions,
    CommitParser,
    ParsedCommit,
)
from semantic_release.enums import LevelBump
from semantic_release.errors import NotAReleaseBranch
from semantic_release.version import Version, VersionTranslator, tags_and_versions
from semantic_release.version.algorithm import _bfs_for_latest_version_in_history

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


def next_version(
    project: str,
    repo: Repo,
    translator: VersionTranslator,
    parser: CommitParser,
) -> Version:
    all_git_tags_as_versions = tags_and_versions(repo.tags, translator)
    all_full_release_tags_and_versions = [
        (t, v) for t, v in all_git_tags_as_versions if not v.is_prerelease
    ]
    log.info(
        "Found %s full releases (excluding prereleases)",
        len(all_full_release_tags_and_versions),
    )

    DEFAULT_VERSION = "0.0.0"

    # Default initial version
    latest_full_release_tag, latest_full_release_version = next(
        iter(all_full_release_tags_and_versions),
        (None, translator.from_string(DEFAULT_VERSION)),
    )

    if latest_full_release_tag is None:
        # the commit id of latest commit
        log.info(
            "No full releases have been made yet, the default version to use is %s",
            latest_full_release_version,
        )
        merge_bases = repo.merge_base(repo.active_branch, repo.active_branch)
    else:
        # the commit id of the tag
        log.info(
            "The last full release was %s, tagged as %r",
            latest_full_release_version,
            latest_full_release_tag,
        )
        merge_bases = repo.merge_base(latest_full_release_tag.name, repo.active_branch)

    merge_base = merge_bases[0]

    if merge_base is None:
        str_tag_name = (
            "None" if latest_full_release_tag is None else latest_full_release_tag.name
        )
        raise ValueError(
            f"The merge_base found by merge_base({str_tag_name}, {repo.active_branch}) "
            "is None"
        )

    latest_full_version_in_history = _bfs_for_latest_version_in_history(
        merge_base=merge_base,
        full_release_tags_and_versions=all_full_release_tags_and_versions,
    )

    commits_since_last_full_release = (
        repo.iter_commits()
        if latest_full_version_in_history is None
        else repo.iter_commits(f"{latest_full_version_in_history.as_tag()}...")
    )

    parsed_levels: set[LevelBump] = set()

    for commit in commits_since_last_full_release:
        parse_result = parser.parse(commit)
        if isinstance(parse_result, ParsedCommit) and parse_result.scope == project:
            parsed_levels.add(parse_result.bump)

    if parsed_levels or not latest_full_version_in_history:
        now = datetime.now()
        return Version(
            now.year,
            now.month,
            int("{}{}{}".format(now.day, now.hour, now.minute)),
            prerelease_token=translator.prerelease_token,
            tag_format=translator.tag_format,
        )
    else:
        return latest_full_version_in_history


def initialize_runtime(repo: Repo, config_file_path="."):
    DEFAULT_CONFIG_FILE = config_file_path + "/pyproject.toml"

    config_path = Path(DEFAULT_CONFIG_FILE)
    config_text = load_raw_config_file(config_path)

    if not config_text:
        raise ValueError(
            f"[tools.semantic_release] needs to be configured in {DEFAULT_CONFIG_FILE}"
        )

    cli_options = GlobalCommandLineOptions(
        noop=False,
        verbosity=1,
        config_file=DEFAULT_CONFIG_FILE,
        strict=False,
    )

    raw_config = RawConfig.model_validate(config_text)

    runtime = RuntimeContext.from_raw_config(
        raw_config, repo=repo, global_cli_options=cli_options
    )

    return runtime


@click.command(
    short_help="Detect and apply a new version",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.option("--project", prompt="Project Tag", help="Required to tag github release.")
@click.option(
    "--project_path",
    help="The path to the project in root, must contain pyproject.toml. e.g. projects/app-cdc-stream-project. ",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="If True: Force release regardless no new features; if False: skip no release.",
)
@click.option(
    "--print_only",
    default=False,
    help="Print the next version and exit",
)
@click.pass_context
def run(
    ctx: click.Context,
    project: str = "dataflow",
    project_path: str = "projects/app-cdc-stream-project",
    force: bool = False,
    print_only: bool = False,
):
    repo = Repo(".", search_parent_directories=True)
    parser = AngularCommitParser(options=AngularParserOptions())
    custom_translator = VersionTranslator(tag_format=project + "_{version}")

    try:
        new_version = next_version(
            project=project, repo=repo, translator=custom_translator, parser=parser
        )

        if print_only:
            log.info(
                "No release will be made in print-only mode. Version to be released is %s",
                new_version.as_tag(),
            )
            ctx.exit(0)

        if new_version in {
            v for _, v in tags_and_versions(repo.tags, custom_translator)
        }:
            if not force:
                log.info(
                    f"No release will be made, {new_version!s} has already been "
                    "released!"
                )
                ctx.exit(0)
            else:
                now = datetime.now()
                new_version = Version(
                    now.year,
                    now.month,
                    int("{}{}{}".format(now.day, now.hour, now.minute)),
                    prerelease_token=custom_translator.prerelease_token,
                    tag_format=custom_translator.tag_format,
                )

                log.warning(
                    "Forcing a %s release due to '--force' command-line option",
                    new_version.as_tag(),
                )
            ## to work on force bump???

        print(new_version.as_tag())  # export to stdout
        runtime = initialize_runtime(repo=repo, config_file_path=project_path)
        parser = runtime.commit_parser
        hvcs_client = runtime.hvcs_client
        assets = runtime.assets
        commit_author = runtime.commit_author
        commit_message = runtime.commit_message
        env = runtime.template_environment
        changelog_file = Path(f"{project_path}/CHANGELOG.md")
        opts = runtime.global_cli_options
        changelog_excluded_commit_patterns = runtime.changelog_excluded_commit_patterns
        version_declarations = runtime.version_declarations
        # Update version in pyproject.toml
        files_with_new_version_written = apply_version_to_source_files(
            repo=repo,
            version_declarations=version_declarations,
            version=new_version,
            noop=opts.noop,
        )

        all_paths_to_add = files_with_new_version_written + (assets or [])

        # Retrive commit history to build CHANGELOG
        rh = ReleaseHistory.from_git_history(
            repo=repo,
            translator=custom_translator,
            commit_parser=parser,
            exclude_commit_patterns=list(changelog_excluded_commit_patterns)
            + [re.compile("^(?:(?!" + project + ").)*$")],
        )

        commit_date = datetime.now()
        try:
            rh = rh.release(
                new_version,
                tagger=commit_author,
                committer=commit_author,
                tagged_date=commit_date,
            )
        except ValueError as ve:
            log.error(str(ve))

        changelog_context = make_changelog_context(
            hvcs_client=hvcs_client, release_history=rh
        )
        changelog_context.bind_to_environment(env)

        updated_paths: list[str] = []

        changelog_text = render_default_changelog_file(env)
        with open(str(changelog_file), "w+", encoding="utf-8") as f:
            f.write(changelog_text)

        updated_paths = [str(changelog_file.relative_to(repo.working_dir))]

        def custom_git_environment() -> ContextManager[None]:
            """
            git.custom_environment is a context manager but
            is not reentrant, so once we have "used" it
            we need to throw it away and re-create it in
            order to use it again
            """
            return (
                nullcontext()
                if not commit_author
                else repo.git.custom_environment(
                    GIT_AUTHOR_NAME=commit_author.name,
                    GIT_AUTHOR_EMAIL=commit_author.email,
                    GIT_COMMITTER_NAME=commit_author.name,
                    GIT_COMMITTER_EMAIL=commit_author.email,
                )
            )

        with custom_git_environment():
            remote_url = runtime.hvcs_client.remote_url(
                use_token=not runtime.ignore_token_for_push
            )
            active_branch = repo.active_branch.name

            repo.git.add(all_paths_to_add)
            repo.git.add(updated_paths)
            repo.git.commit(
                m=project + "_" + commit_message.format(version=new_version),
                date=int(commit_date.timestamp()),
            )
            repo.git.tag("-a", new_version.as_tag(), m=new_version.as_tag())
            repo.git.push(remote_url, active_branch)
            repo.git.push("--tags", remote_url, active_branch)

        # Release and update release note with the CHANGELOG generated above
        release = rh.released[new_version]
        # Use a new, non-configurable environment for release notes -
        # not user-configurable at the moment
        release_note_environment = environment(template_dir=runtime.template_dir)
        changelog_context.bind_to_environment(release_note_environment)
        release_notes = render_release_notes(
            template_environment=release_note_environment,
            version=new_version,
            release=release,
        )
        try:
            release_id = hvcs_client.create_or_update_release(
                tag=new_version.as_tag(),
                release_notes=release_notes,
                prerelease=new_version.is_prerelease,
            )
            log.info("Released with %s", release_id)
        except Exception as e:
            log.exception(e)

    except NotAReleaseBranch:
        log.info(
            "Not on release branch. No release will be made, exit semantic release."
        )

    except TypeError as te:
        if "HEAD is a detached symbolic reference" in str(te):
            now = datetime.now()
            possible_version = "{}.{}.{}{}{}".format(
                now.year, now.month, now.day, now.hour, now.minute
            )
            log.info(
                str(te)
                + f"\nPossible version to release is {project}_{possible_version}."
                + "\nNo release will be made, exit semantic release. "
            )
        else:
            raise
    except Exception as e:
        log.error(str(e))


if __name__ == "__main__":
    run()

"""
poetry run python semantic-release.py --project=project_1 --project_path=app/project_1
poetry run python semantic-release.py --project=project_2 --project_path=app/project_2
"""
