from typing import ClassVar, Union, List, Dict

class HelpCmd:
    """
    A class to manage help commands.

    Should only be used inside plugin files which execute on startup.
    """

    _helper: ClassVar[Dict[str, Dict[str, Union[str, bool, List[str], None]]]] = {}

    @classmethod
    def set_help(  # noqa: PLR0913
        cls,
        command: str,
        description: Union[str, None],
        allow_global: bool,  # noqa: FBT001
        allow_non_admin: bool,  # noqa: FBT001
        alias: Union[str, List[str]] = "N/A",
    ) -> None:
        """Set help information for a command.

        Parameters:
            command (str):
                The name of the command.

            alias (Union[str, List[str], None]):
                The alias(es) of the command.

            description (str):
                The description of the command.

            allow_global (bool):
                Commands that can be used by non-admins if global mode is enabled in options.

            allow_non_admin (bool):
                Commands that are only available to non-admin users and if global mode is disabled in option.

        Returns: None
        """
        cls._helper[command] = {
            "alias": alias,
            "description": description,
            "allow_global": allow_global,
            "allow_non_admin": allow_non_admin,
        }

    @classmethod
    def get_help(cls, command: str) -> Union[Dict[str, Union[str, bool, List[str], None]], None]:
        """Get help information for a command.

        Parameters:
            command (str): The name of the command.

        Returns:
            dict: A dictionary containing the alias and description of the command.
        """
        return cls._helper.get(command)

    @classmethod
    def get_cmds(cls) -> List[str]:
        """Get a list of all commands.

        Returns:
            list: A list of all commands.
        """
        return list(cls._helper.keys())

    @classmethod
    def get_non_admin_cmds(cls) -> List[str]:
        """Get a list of non-admin commands available to all subscribed users

        Returns:
            list: A list of allow_non_admin commands.
        """
        return [command for command, data in cls._helper.items() if data["allow_non_admin"]]

    @classmethod
    def get_global_cmds(cls) -> List[str]:
        """Get global commands that are usable if global mode is set to enable in options

        Returns:
            list: A list of allow_global commands.
        """
        return [command for command, data in cls._helper.items() if data["allow_global"]]
