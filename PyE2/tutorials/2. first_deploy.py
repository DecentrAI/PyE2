"""
This is a simple example of how to use the PyE2 library.

In this example, we connect to the network, choose a node and
    deploy a plugin that will extract frames from a video stream.
"""

from PyE2 import Session, Pipeline, Instance, Payload

from time import sleep


def instance_on_data(pipeline: Pipeline, data: Payload):
  # the images can be extracted from the Payload object
  # PIL needs to be installed for this to work
  images = data.get_image_as_PIL()
  if images is not None:
    images[0].save('frame.jpg')


if __name__ == '__main__':
  # create a session
  # the network credentials are read from the .env file automatically
  session: Session = Session(encrypt_comms=True)

  while session.get_active_nodes() == []:
    session.P("Waiting for nodes to send heartbeats...")
    sleep(1)

  chosen_node = session.get_active_nodes()[0]

  # we have our node, let's deploy a plugin

  # first, we create a pipeline
  # we will use the video file data source, since we want to extract frames from a video
  pipeline: Pipeline = session.create_pipeline(
    e2id=chosen_node,
    name='first_deploy',
    data_source='VideoFile',
    config={
      'URL': "https://www.dropbox.com/scl/fi/8z2wpeelhav3k2dv8bb5p/Cars_3.mp4?rlkey=imv415rr3j1tx3zstpurlxkqb&dl=1"
    }
  )

  # next, we deploy a plugin instance
  # we will use the view scene plugin, which essentially generates payloads with frames from the video
  # to consume the payloads generated by the plugin, we need to specify a callback function
  instance: Instance = pipeline.start_plugin_instance(
    signature='VIEW_SCENE_01',
    instance_id='inst01',
    on_data=instance_on_data,
    # we can specify the configuration for the plugin instance as kwargs
    process_delay=3,
    # we can also specify if the payloads should be encrypted
    # if so, only the creator of this pipeline, in our case us, will be able to decrypt the payloads
    encrypt_payload=True,
  )

  # run the program for 30 seconds, then close the session
  session.run(wait=30, close_session=True, close_pipelines=True)
  session.P("Main thread exiting...")
