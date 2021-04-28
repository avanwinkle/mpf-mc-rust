from mpf.core.custom_code import CustomCode

import grpc
from mpfdmc.server.server_pb2_grpc import MediaControllerStub
from mpfdmc.server.server_pb2 import SlideAddRequest, WidgetAddRequest, ShowSlideRequest, SlideRemoveRequest, Widget
from mpfdmc.config_players.rust_slide_player import RustSlidePlayer
from mpfdmc.config_players.rust_widget_player import RustWidgetPlayer

# MPF Direct MC is not yet integrated with the YAML 'slides:' and 'widgets:' syntax.
# Projects must include a custom_code/slides.py file that exports two dicts
# (named slides and widgets) with names as keys, and values that are functions
# which return SlideAddRequest/WidgetAddRequest instances
from custom_code.slides import slides, widgets

class MCRustWindow(CustomCode):

    def __init__(self, machine, name):
        """Create custom code to interactions between MPF and Rust-MC"""
        super().__init__(machine, "MCRustWindow")

        # Connections to the Rust server
        self._channel = grpc.insecure_channel('localhost:50051')
        self.mc = MediaControllerStub(self._channel)

        self._slides = {}
        self._widgets = {}
        self._current_slide = None
        self.enabled = True

        # Define RustSlidePlayer as the slide_player for the machine
        setattr(self.machine, 'slide_player',
            RustSlidePlayer(self.machine))
        # Define RustWidgetPlayer as the widget_player for the machine
        setattr(self.machine, 'widget_player',
            RustWidgetPlayer(self.machine))

        self.machine.events.add_handler("player_score", self._on_score)

    def on_load(self):
        self.ready = True
        # Mock out to pretend that this is a display target. Requires all the
        # display targets defined in the config to be present here.
        self.machine.targets = { 'default': self }

    def _on_score(self, **kwargs):
        value = kwargs['value']
        self.info_log("Updating score to new value {}".format(value))
        if "score_widget" in self._widgets:
            self._widgets["score_widget"].label_widget.text = "{:0>2,}".format(value)
        else:
            self._widgets["score_widget"] = widgets['score_widget'](value)


    def add_widgets_to_slide(self, settings, **kwargs):
        widget_add_request = WidgetAddRequest()
        # TODO: Accept a target slide
        slide_id = self._current_slide.slide_id
        widget_add_request.slide_id = slide_id
        for widget_name, s in settings.items():
            widget_add_request.widgets.append(self.get_widget(widget_name))

        self.mc.AddWidgetsToSlide(widget_add_request)

    def get_screen(self, __slide_name):
        """Method from Display that returns which screen a given slide is attached to. Not used."""
        return self

    def on_slide_play(self):
        """Callback method called after the slide is rendered.
        Used in MC for widgets
        to trigger animations based on slide appearing. Not used yet."""

    def get_slide(self, slide_name):
        return self._slides.get(slide_name)
        # self.warning_log("Slide '{}' is unconfigured in Rust slides".format(slide_name))

    def get_widget(self, widget_name):
        # Don't cache widgets?
        if widgets.get(widget_name):
            return widgets[widget_name]()
        raise KeyError("Widget '{}' is unconfigured in Rust widgets".format(widget_name))


    def show_slide(self, **kwargs):
        # TODO: Any difference in behavior between show and add+show?
        self.add_and_show_slide(**kwargs)

    def add_and_show_slide(self, slide_name, **kwargs):
        # Fetch a slide request with the pre-populated widgets
        slide = self.get_slide(slide_name)
        # Generate a slide instance for the request
        if not slide:
            slide_request = slides[slide_name](
                player=self.machine.game.player if self.machine.game else {}
            )
            slide = self.mc.AddSlide(slide_request)

        # Generate a request to show the slide instance
        show_slide_request = ShowSlideRequest()
        # Attach the slide id to the request so mc knows which slide to show
        show_slide_request.slide_id = slide.slide_id
        # Show it!
        self.mc.ShowSlide(show_slide_request)
        self._current_slide = slide
        self._slides[slide_name] = slide
        return slide

    def remove_slide(self, slide_name, __transition_config=None):
        self.info_log("Trying to remove slide {}".format(slide_name))
        if slide_name in self._slides:
            slide = self._slides[slide_name]
            remove_slide_request = SlideRemoveRequest()
            remove_slide_request.slide_id = slide.slide_id
            self.mc.RemoveSlide(remove_slide_request)
            # Wait until remove successful before deleting, in case async issues
            # del self._slides[slide_name]


    """
        # The below is demo/test code
        slide_add_request = SlideAddRequest()
        widget = Widget()
        widget.x = 5
        widget.y = 5
        widget.z = 2
        widget.rectangle_widget.color.red = 0.0
        widget.rectangle_widget.color.blue = 1.0
        widget.rectangle_widget.color.green = 0.5
        widget.rectangle_widget.color.alpha = 1.0
        widget.rectangle_widget.width = 500
        widget.rectangle_widget.height = 300
        slide_add_request.widgets.append(widget)

        widget = Widget()
        widget.x = 10
        widget.y = 10
        widget.z = 5
        #widget.video_widget.path = "/home/jan/Downloads/Biking_Girl_Alpha.mov"
        widget.video_widget.path = "/Users/anthony/Movies/createprofile_1.mp4"
        slide_add_request.widgets.append(widget)

        new_slide = stub.AddSlide(slide_add_request)
        slide_id = new_slide.slide_id

        # Slide has been created now lets add more widgets
        widget_add_request = WidgetAddRequest()
        widget_add_request.slide_id = slide_id

        widget = Widget()
        widget.x = 50
        widget.y = 50
        widget.z = 4
        widget.image_widget.path = "/Users/anthony/Pictures/mM0HX1A.jpg"
        widget_add_request.widgets.append(widget)

        widget = Widget()
        widget.x = 20
        widget.y = 150
        widget.z = 5
        widget.label_widget.color.red = 1.0
        widget.label_widget.color.blue = 0.0
        widget.label_widget.color.green = 0.0
        widget.label_widget.color.alpha = 1.0
        widget.label_widget.text = "Hello Schmoopie!"
        widget.label_widget.font_name = "DejaVuSerif.ttf"
        widget.label_widget.font_size = 32
        widget_add_request.widgets.append(widget)

        widget = Widget()
        widget.x = 30.0
        widget.y = 30.0
        widget.z = 6
        widget.line_widget.color.red = 1.0
        widget.line_widget.color.blue = 0.0
        widget.line_widget.color.green = 0.0
        widget.line_widget.color.alpha = 1.0
        widget.line_widget.x1 = 3.0
        widget.line_widget.y1 = 50.0
        widget.line_widget.x2 = 150.0
        widget.line_widget.y2 = 300.0
        widget.line_widget.width = 10.0
        widget_add_request.widgets.append(widget)

        stub.AddWidgetsToSlide(widget_add_request)

        show_slide_request = ShowSlideRequest()
        show_slide_request.slide_id = slide_id
        stub.ShowSlide(show_slide_request)
    """
