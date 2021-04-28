# Copyright 2021 Paradigm Tilt

from mpfdmc.config_players.rust_config_player import RustConfigPlayer


class RustSlidePlayer(RustConfigPlayer):
    """A SlidePlayer instance.

    Required because without a BCP client registered, MPF will not generate the
    various MC player events like "slides_play" and "sounds_play". Someday I'll
    figure out how to work around that. In the meantime, this class exists.
    """

    config_file_section = 'slide_player'
    show_section = 'slides'
    machine_collection_name = 'slides'
    allow_placeholders_in_keys = True

    def play(self, settings, context: str, calling_context: str, priority: int = 0, **kwargs):
        super().play(settings, context, calling_context, priority=0, **kwargs)
        # Assume just one target for now
        target_name = 'default'

        target = self.machine.targets[target_name]
        instance_dict = self._get_instance_dict(context)

        if target_name not in instance_dict:
            instance_dict[target_name] = {}

        for slide_name, s in settings.items():
            action = s['action']
            if action == 'play':
                slide = target.add_and_show_slide(slide_name, **s)
                instance_dict[target_name][slide_name] = slide
                return slide
            if action == 'remove' and slide_name in instance_dict.get(target_name, {}):
                del instance_dict[target_name][slide]
                return target.remove_slide(slide_name, **s)
        return None


    def clear_context(self, context):
        instance_dict = self._get_instance_dict(context)
        for target_name, slides in instance_dict.items():
            target = self.machine.targets[target_name]
            for slide_name in slides.keys():
                target.remove_slide(slide_name)

        self._reset_instance_dict(context)