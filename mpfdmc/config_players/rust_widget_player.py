from mpfdmc.config_players.rust_config_player import RustConfigPlayer

# Can't inherit directly from McWidgetPlayer because that has Kivy dependencies
class RustWidgetPlayer(RustConfigPlayer):
    """A WidgetPlayer instance.

    Required because without a BCP client registered, MPF will not generate the
    various MC player events like "slides_play" and "sounds_play". Someday I'll
    figure out how to work around that. In the meantime, this class exists.
    """

    config_file_section = 'widget_player'
    show_section = 'widgets'
    machine_collection_name = 'widgets'
    allow_placeholders_in_keys = True

    def play(self, settings, context: str, calling_context: str, priority: int = 0, **kwargs):
        # Assume just one target for now
        target = self.machine.targets['default']
        target.add_widgets_to_slide(settings)
