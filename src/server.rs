use tonic::{transport::Server, Request, Response, Status};

use mpf::media_controller_server::{MediaController, MediaControllerServer};
use mpf::*;

use std::sync::Arc;
use std::sync::Mutex;

pub mod mpf {
    tonic::include_proto!("mpf");
}

#[derive(Debug)]
pub struct MyMediaController {
    scene: Arc<super::scene::Scene>
}

#[tonic::async_trait]
impl MediaController for MyMediaController {

    async fn add_slide(&self, _request: Request<SlideAddRequest>) ->
    Result<Response<SlideAddResponse>, Status> {
        let mut next_slide_id = self.scene.next_slide_id.lock().unwrap();
        *next_slide_id += 1;
        let empty_slide = Arc::new(Mutex::new(super::scene::Slide {
            widgets: vec![]
        }));
        self.scene.slides.lock().unwrap().insert(*next_slide_id, empty_slide);

        Ok(Response::new(SlideAddResponse{
            slide_id: *next_slide_id
        }))     
    }

    async fn show_slide(&self, request: tonic::Request<ShowSlideRequest>) -> 
    Result<tonic::Response<ShowSlideResponse>, tonic::Status> {
        let req = request.into_inner();
        println!("Show slide {}", req.slide_id);
       
        let mut current_slide = self.scene.current_slide.lock().unwrap();
        match self.scene.slides.lock().unwrap().get_mut(&req.slide_id) {
            Some(slide) => {
                *current_slide = slide.clone();

                Ok(Response::new(ShowSlideResponse{}))
            }
            None => {
                Err(Status::invalid_argument("Could not find slide"))
            }
        }
    }

    async fn add_widgets_to_slide(&self, request: tonic::Request<WidgetAddRequest>) ->
    Result<tonic::Response<WidgetAddResponse>, tonic::Status> {
        let req = request.into_inner();
        println!("Slide {} Text: {}", req.slide_id, req.text);
       
        match self.scene.slides.lock().unwrap().get_mut(&req.slide_id) {
            Some(slide) => {
                let new_widget = super::scene::Widget {
                    x: 10.0,
                    y: 100.0,
                    z: 1,
                    id: req.slide_id,
                    color: [1.0, 0.0, 0.0, 1.0],
                    widget: super::scene::WidgetType::Text {
                        text: req.text
                    }
                };
                {
                    let mut slide = slide.lock().unwrap();
                    slide.widgets.push(new_widget);
                }
                Ok(Response::new(WidgetAddResponse{}))
            }
            None => {
                Err(Status::invalid_argument("Could not find slide"))
            }
        }
    }
}

pub async fn serve(scene: Arc<super::scene::Scene>) {
    let addr = "[::1]:50051".parse().unwrap();
    let mc = MyMediaController{
        scene
    };

    Server::builder()
        .add_service(MediaControllerServer::new(mc))
        .serve(addr)
        .await.unwrap();
}