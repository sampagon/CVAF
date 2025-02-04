from framework import Framework
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
time.sleep(4)

coords = framework.vision_system("Find where it says Men")
framework.mouse_move(coordinate=coords)
framework.left_click()
framework.mouse_move(coordinate=[0,0])
time.sleep(2)

coords = framework.vision_system("Find where it says Shoes")
framework.mouse_move(coordinate=coords)
framework.left_click()
time.sleep(2)

framework.key(text="Page_Down")
coords = framework.vision_system("Find where it says Nike Air Force 1'07")
framework.mouse_move(coordinate=coords)
framework.left_click()
time.sleep(2)

coords = framework.vision_system("Find the Notify Me button")
framework.mouse_move(coordinate=coords)
framework.left_click()
time.sleep(1)

coords = framework.vision_system("Find the Email Address Box")
framework.mouse_move(coordinate=coords)
framework.left_click()
framework.type(text="johndoe@example.com")
time.sleep(1)

coords = framework.vision_system("Find the Submit button")
framework.mouse_move(coordinate=coords)
framework.left_click()
time.sleep(1)

framework.stop()