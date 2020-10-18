import appdaemon.plugins.hass.hassapi as hass

#
# Light Ramp app
#
# Simple test app. This app on any light being turned on.
#
# The light is then dimmed in brightness until it it nearly off
# and then it is increased until full brightness. This is repeated
# over and over again.
#
# Caveat: This app is only working properly with 1 single light.
#         The step value is currently global for all lights
#
#         Besides, this app is just to check the different timers.
#         Otherwise it is pretty useseless.
#
# Args:
#

def clamp(n, low, high):
    return max(low, min(high, n))

class LightRamp(hass.Hass):

    def initialize(self):

        self.light_change_listener = self.listen_state(self.light_changed, "light", attribute='state')
        self.threshold = (5,255)
        self.step = -5
        self.active = dict()
        self.log("Light Ramp is up and runnnig")


    def light_changed(self, entity, attribute, old, new, kwargs):

        self.log("State changed entity '{}' attribute '{}' old '{}' new '{}'".format(entity,attribute,old,new))

        if new == 'off' and entity in self.active:
            self.cancel_timer(self.active[entity])

        elif new == 'on' and old == 'off':
            self.active[entity] = self.run_every(self.adjust_light, "now", 1, entity=entity)


    def adjust_light(self, args):

        entity = args['entity']
        brightness = self.get_state(entity, attribute='brightness')
        self.log("adjust light old brightness {}".format(brightness))
        brightness = clamp(brightness + self.step, self.threshold[0], self.threshold[1])

        if any(brightness == t for t in self.threshold):
            self.step *= -1

        self.log("adjust light new brightness {} step {}".format(brightness,self.step))
        self.turn_on(entity, brightness=brightness)
