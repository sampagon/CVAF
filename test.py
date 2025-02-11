from framework.framework import Framework
import time

framework = Framework()
framework.start()
time.sleep(1)

coords = framework.vision_system("Find the firefox icon")
framework.mouse_move(coordinate=coords)
framework.left_click()
time.sleep(1)

coords = framework.vision_system("Find the search or enter address bar")
framework.mouse_move(coordinate=coords)
framework.left_click()
time.sleep(1)

framework.type(text="nike.com")
framework.key(text="Return")

framework.stop()