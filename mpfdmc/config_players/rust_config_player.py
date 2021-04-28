from mpf.config_players.device_config_player import DeviceConfigPlayer

# Can't inherit directly from McWidgetPlayer because that has Kivy dependencies
class RustConfigPlayer(DeviceConfigPlayer):

    config_file_section = None
    show_section = None
    machine_collection_name = None
    allow_placeholders_in_keys = True


    def __init__(self, machine):
        """Initialise config player."""
        super().__init__(machine)

        # init_phase_1 has already happened by the time we arrive here, so manually initialize
        self._initialize_mode_handlers()
        self._initialise_system_wide()

    def _initialise_system_wide(self, **kwargs):
        """Override/ignore all the default system_wide behavior, MPF doesn't expect slide/widget players."""
        del kwargs
        self.device_collection = None

    def get_express_config(self, value):
        # No express configs here
        return {}

    def play(self, settings, context: str, calling_context: str, priority: int = 0, **kwargs):
        """Base method for play, setting up context universally."""
        if context not in self.instances:
            self.instances[context] = dict()
        if self.config_file_section not in self.instances[context]:
            self.instances[context][self.config_file_section] = dict()
