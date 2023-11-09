"""
rydnr/sandbox/artifact/infrastructure/local_sandbox_artifact.py

This file defines LocalSandboxArtifact

Copyright (C) 2023-today rydnr's rydnr/sandbox-artifact-infrastructure

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from pythoneda import listen
from pythoneda.shared.artifact import LocalArtifact
from pythoneda.shared.artifact.artifact.events import (
    ArtifactChangesCommitted,
    ArtifactCommitPushed,
    ArtifactCommitTagged,
    ArtifactTagPushed,
)
from pythoneda.shared.artifact.events import (
    CommittedChangesPushed,
    CommittedChangesTagged,
    StagedChangesCommitted,
    TagPushed,
)
from pythoneda.shared.nix_flake import (
    FlakeUtilsNixFlake,
    License,
    NixosNixFlake,
    PythonedaSharedPythonedaBannerNixFlake,
)
from pythoneda.shared.nix_flake.licenses import Gpl3


class LocalSandboxArtifact(LocalArtifact):

    """
    A locally-cloned SandboxArtifact.

    Class name: LocalSandboxArtifact

    Responsibilities:
        - Represent the Sandbox artifact.
        - React upon incoming artifact events from Sandbox's dependencies.

    Collaborators:
        - pythoneda.shared.artifact.Artifact: Common logic for Artifacts.
        - rydnr.sandbox.artifact.application.SandboxArtifactApp: To initialize this class.
    """

    _singleton = None

    def __init__(self, folder: str):
        """
        Creates a new LocalSandboxArtifact instance.
        :param folder: The folder with the Sandbox repository.
        :type folder: str
        """
        flake_utils = FlakeUtilsNixFlake.default()
        nixos = NixosNixFlake.default()
        banner = PythonedaSharedPythonedaBannerNixFlake.default()
        inputs = [flake_utils, nixos, banner]
        version = self.find_out_version(folder)
        super().__init__(
            "pythoneda-sandbox-python",
            self.find_out_version(folder),
            self.url_for,
            inputs,
            "pythoneda",
            "pythoneda-sandbox Python package",
            "https://github.com/pythoneda-sandbox/python",
            License.from_id(
                Gpl3.license_type(),
                "2023",
                "rydnr",
                "https://github.com/pythoneda-sandbox/python",
            ),
            ["rydnr <github@acm-sl.org>"],
            2023,
            "rydnr",
            folder,
        )

    @classmethod
    def initialize(cls, folder: str):
        """
        Initializes the singleton.
        :param folder: The repository folder.
        :type folder: str
        """
        cls._singleton = LocalSandboxArtifact(folder)

    @classmethod
    def instance(cls):
        """
        Retrieves the singleton instance.
        :return: Such instance.
        :rtype: Ports
        """
        result = cls._singleton
        if result is None:
            LocalSandboxArtifact.logger().error(
                "LocalSandboxArtifact not yet bound to a local folder. "
            )
        return result

    def url_for(self, version: str) -> str:
        """
        Retrieves the url for given version.
        :param version: The version.
        :type version: str
        :return: The url.
        :rtype: str
        """
        return (
            f"https://github.com/pythoneda-sandbox/python-artifact/{version}?dir=python"
        )

    @classmethod
    @listen(StagedChangesCommitted)
    async def listen_StagedChangesCommitted(
        cls, event: StagedChangesCommitted
    ) -> CommittedChangesPushed:
        """
        Gets notified of a StagedChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.StagedChangesCommitted
        :return: An event notifying the commit has been pushed.
        :rtype: pythoneda.shared.artifact.events.CommittedChangesPushed
        """
        return await cls.instance().commit_push(event)

    @classmethod
    @listen(CommittedChangesPushed)
    async def listen_CommittedChangesPushed(
        cls, event: CommittedChangesPushed
    ) -> CommittedChangesTagged:
        """
        Gets notified of a CommittedChangesPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.CommitedChangesPushed
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact.events.CommittedChangesTagged
        """
        return await cls.instance().commit_tag(event)

    @classmethod
    @listen(CommittedChangesTagged)
    async def listen_CommittedChangesTagged(
        cls, event: CommittedChangesTagged
    ) -> TagPushed:
        """
        Gets notified of a CommittedChangesTagged event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.CommittedChangesTagged
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact.events.TagPushed
        """
        return await cls.instance().tag_push(event)

    @classmethod
    @listen(TagPushed)
    async def listen_TagPushed(cls, event: TagPushed) -> ArtifactChangesCommitted:
        """
        Gets notified of a TagPushed event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.TagPushed
        :return: An event notifying the changes in the artifact have been committed.
        :rtype: pythoneda.shared.artifact.artifact.events.ArtifactChangesCommitted
        """
        return await cls.instance().artifact_commit_from_TagPushed(event)

    @classmethod
    @listen(ArtifactChangesCommitted)
    async def listen_ArtifactChangesCommitted(
        cls, event: ArtifactChangesCommitted
    ) -> ArtifactCommitPushed:
        """
        Gets notified of an ArtifactChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.artifact.events.ArtifactChangesCommitted
        :return: An event notifying the commit in the artifact repository has been pushed.
        :rtype: pythoneda.shared.artifact.artifact.events.ArtifactCommitPushed
        """
        return await cls.instance().artifact_commit_push(event)

    @classmethod
    @listen(ArtifactCommitPushed)
    async def listen_ArtifactCommitPushed(
        cls, event: ArtifactCommitPushed
    ) -> ArtifactCommitTagged:
        """
        Gets notified of an ArtifactCommitPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.artifact.events.ArtifactCommitPushed
        :return: An event notifying the commit in the artifact repository has been tagged.
        :rtype: pythoneda.shared.artifact.artifact.events.ArtifactCommitTagged
        """
        return await cls.instance().artifact_commit_tag(event)

    @classmethod
    @listen(ArtifactCommitTagged)
    async def listen_ArtifactCommitTagged(
        cls, event: ArtifactCommitTagged
    ) -> ArtifactTagPushed:
        """
        Gets notified of an ArtifactCommitTagged event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_commit.events.ArtifactCommitTagged
        :return: An event notifying the tag in the artifact has been pushed.
        :rtype: pythoneda.shared.artifact_commit.events.ArtifactTagPushed
        """
        return await cls.instance().artifact_tag_push(event)

    @classmethod
    @listen(ArtifactTagPushed)
    async def listen_ArtifactTagPushed(
        cls, event: ArtifactTagPushed
    ) -> ArtifactChangesCommitted:
        """
        Listens to ArtifactTagPushed event to check if affects any of its dependencies.
        In such case, it creates a commit with the dependency change.
        :param event: The event.
        :type event: pythoneda.shared.artifact.artifact.events.ArtifactTagPushed
        :return: An event representing the commit.
        :rtype: pythoneda.shared.artifact.artifact.events.ArtifactChangesCommitted
        """
        return await cls.instance().artifact_commit_from_ArtifactTagPushed(event)
