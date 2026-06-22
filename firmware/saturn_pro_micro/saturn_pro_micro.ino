#include <Keyboard.h>

/*
  SATURN Pro Micro Macro Deck
  - 6 botones fisicos
  - Cada boton va entre PIN y GND
  - Usa INPUT_PULLUP, no hace falta resistencia externa
  - Envia F13, F14, F15, F16, F17 y F18 como taps cortos
  - Loop no bloqueante: no usa delay()

  Si tu cableado usa otros pines, cambia solo la tabla BUTTONS.
*/

#ifndef KEY_F13
#define KEY_F13 (0x80 + 0x68)
#define KEY_F14 (0x80 + 0x69)
#define KEY_F15 (0x80 + 0x6A)
#define KEY_F16 (0x80 + 0x6B)
#define KEY_F17 (0x80 + 0x6C)
#define KEY_F18 (0x80 + 0x6D)
#endif

#define ENABLE_SERIAL_DEBUG 0
#define ENABLE_ACTIVITY_LED 1

#ifndef LED_BUILTIN
#define LED_BUILTIN 17
#endif

const unsigned long DEBOUNCE_MS = 25;
const unsigned long TAP_MS = 14;
const unsigned long LED_PULSE_MS = 70;

struct ButtonConfig {
  byte pin;
  byte keyCode;
  bool repeatWhileHeld;
  unsigned int repeatDelayMs;
  unsigned int repeatIntervalMs;
};

const byte BUTTON_COUNT = 6;

const ButtonConfig BUTTONS[BUTTON_COUNT] = {
  // pin, key,    repeat, delay, interval
  {2, KEY_F13, false, 450, 120},
  {3, KEY_F14, false, 450, 120},
  {4, KEY_F15, false, 450, 120},
  {5, KEY_F16, false, 450, 120},
  {6, KEY_F17, false, 450, 120},
  {7, KEY_F18, false, 450, 120}
};

bool stablePressed[BUTTON_COUNT];
bool lastReading[BUTTON_COUNT];
bool tapActive[BUTTON_COUNT];

unsigned long lastChangeAt[BUTTON_COUNT];
unsigned long releaseAt[BUTTON_COUNT];
unsigned long nextRepeatAt[BUTTON_COUNT];
unsigned long activityLedUntil = 0;

void setup() {
#if ENABLE_SERIAL_DEBUG
  Serial.begin(115200);
#endif

#if ENABLE_ACTIVITY_LED
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
#endif

  for (byte i = 0; i < BUTTON_COUNT; i++) {
    pinMode(BUTTONS[i].pin, INPUT_PULLUP);
    stablePressed[i] = false;
    lastReading[i] = false;
    tapActive[i] = false;
    lastChangeAt[i] = 0;
    releaseAt[i] = 0;
    nextRepeatAt[i] = 0;
  }

  Keyboard.begin();
}

void loop() {
  const unsigned long now = millis();

  releaseFinishedTaps(now);
  updateActivityLed(now);
  readButtons(now);
}

void readButtons(unsigned long now) {
  for (byte i = 0; i < BUTTON_COUNT; i++) {
    const bool readingPressed = digitalRead(BUTTONS[i].pin) == LOW;

    if (readingPressed != lastReading[i]) {
      lastReading[i] = readingPressed;
      lastChangeAt[i] = now;
    }

    if (now - lastChangeAt[i] < DEBOUNCE_MS) {
      continue;
    }

    if (readingPressed != stablePressed[i]) {
      stablePressed[i] = readingPressed;

      if (stablePressed[i]) {
        sendTap(i, now);
        nextRepeatAt[i] = now + BUTTONS[i].repeatDelayMs;
      }
    }

    if (
      stablePressed[i] &&
      BUTTONS[i].repeatWhileHeld &&
      timeReached(now, nextRepeatAt[i])
    ) {
      sendTap(i, now);
      nextRepeatAt[i] = now + BUTTONS[i].repeatIntervalMs;
    }
  }
}

void sendTap(byte index, unsigned long now) {
  if (tapActive[index]) {
    Keyboard.release(BUTTONS[index].keyCode);
    tapActive[index] = false;
  }

  Keyboard.press(BUTTONS[index].keyCode);
  tapActive[index] = true;
  releaseAt[index] = now + TAP_MS;
  activityLedUntil = now + LED_PULSE_MS;

#if ENABLE_SERIAL_DEBUG
  Serial.print("Button ");
  Serial.print(index + 1);
  Serial.print(" -> F");
  Serial.println(13 + index);
#endif
}

void releaseFinishedTaps(unsigned long now) {
  for (byte i = 0; i < BUTTON_COUNT; i++) {
    if (tapActive[i] && timeReached(now, releaseAt[i])) {
      Keyboard.release(BUTTONS[i].keyCode);
      tapActive[i] = false;
    }
  }
}

void updateActivityLed(unsigned long now) {
#if ENABLE_ACTIVITY_LED
  digitalWrite(LED_BUILTIN, timeReached(now, activityLedUntil) ? LOW : HIGH);
#endif
}

bool timeReached(unsigned long now, unsigned long target) {
  return (long)(now - target) >= 0;
}
