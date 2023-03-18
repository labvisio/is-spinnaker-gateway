import cv2

from is_spinnaker_gateway.conf.options_pb2 import ColorProcessingAlgorithm
from is_spinnaker_gateway.driver.spinnaker.spinnaker import SpinnakerDriver


def main():
    driver = SpinnakerDriver(
        color_algorithm=ColorProcessingAlgorithm.BILINEAR,
        onboard_color_processing=False,
    )
    driver.connect(ip="10.20.6.0")
    driver.start_capture()

    while True:
        image = driver.grab_image(wait=True)
        if image is not None:
            array = driver.to_array(image=image)
            if image is not None:
                cv2.imshow('frame', array)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    driver.stop_capture()
    driver.close()


if __name__ == "__main__":
    main()
