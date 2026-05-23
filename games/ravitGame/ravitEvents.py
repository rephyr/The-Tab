"""
Event handlers for RavitGame.

Mixed into RavitGame via RavitEventsMixin. Each _event* method returns a Finnish
detail string describing what happened, or None if the event fizzled (e.g. no
valid target). _tryFireEvent rolls for an event and calls _applyEvent to dispatch.
"""
import random
from games.ravitGame.horses import Horse
import games.ravitGame.eventTypes as ET
from core.events import HorseEventFiredEvent

_POS_EVENTS  = [ET.BOOST, ET.MOTIVATED, ET.OVERTAKE]
_POS_WEIGHTS = [4, 4, 3]
_NEG_EVENTS  = [ET.DEATH, ET.BACKWARDS, ET.STUMBLE, ET.SLIP_FALL, ET.CONFUSED,
                ET.LIGHTNING, ET.DRUNK_FAN, ET.HORSE_KICK, ET.HORSE_SHOE]
_NEG_WEIGHTS = [1, 3, 3, 3, 2, 2, 2, 3, 2]


class RavitEventsMixin:
    """All random-event logic for RavitGame. Expects self to be a RavitGame instance."""

    def _tryFireEvent(self, horse: Horse) -> None:
        """Roll for a random event; positive events scale with luck, negative scale inversely."""
        if self._roundNumber <= 1 or horse.id in self._eventedThisRound:
            return
        jockey = self._jockeyForHorse(horse)
        baseChance = self._getConfig("eventChance", 0.15) * (jockey.eventChanceMultiplier if jockey else 1.0)
        posChance = min(baseChance * (horse.luck / 3.0), 0.95)
        negChance = min(baseChance * ((6 - horse.luck) / 3.0), 0.95)

        r = random.random()
        if r < posChance:
            eventType = random.choices(_POS_EVENTS, weights=_POS_WEIGHTS)[0]
        elif r < posChance + negChance:
            eventType = random.choices(_NEG_EVENTS, weights=_NEG_WEIGHTS)[0]
        else:
            return

        detail = self._applyEvent(horse, eventType)
        if detail is None:
            return

        if eventType == ET.LIGHTNING and horse.status == "dead":
            eventType = ET.LIGHTNING_DEATH

        self._eventedThisRound.add(horse.id)
        print(f"  *** {detail}")
        self._roundEvents.append({"horseName": horse.name, "eventType": eventType, "detail": detail})
        self.emit(HorseEventFiredEvent(
            roundNumber=self._roundNumber,
            horseId=horse.id,
            horseName=horse.name,
            eventType=eventType,
            detail=detail,
        ))

    def _applyEvent(self, horse: Horse, eventType: str) -> str | None:
        """Dispatch to the correct event handler; returns detail string or None if event fizzled."""
        tl = self._getConfig("trackLength", 20)
        dispatch = {
            ET.BOOST:      lambda: self._eventBoost(horse, tl),
            ET.MOTIVATED:  lambda: self._eventMotivated(horse),
            ET.OVERTAKE:   lambda: self._eventOvertake(horse, tl),
            ET.DEATH:      lambda: self._eventDeath(horse),
            ET.BACKWARDS:  lambda: self._eventBackwards(horse),
            ET.STUMBLE:    lambda: self._eventStumble(horse),
            ET.SLIP_FALL:  lambda: self._eventSlipFall(horse),
            ET.CONFUSED:   lambda: self._eventConfused(horse),
            ET.LIGHTNING:  lambda: self._eventLightning(horse),
            ET.DRUNK_FAN:  lambda: self._eventDrunkFan(),
            ET.HORSE_KICK: lambda: self._eventHorseKick(horse),
            ET.HORSE_SHOE: lambda: self._shoeFallsOff(),
        }
        fn = dispatch.get(eventType)
        return fn() if fn else None

    # ------------------------------------------------------------------
    # Positive events
    # ------------------------------------------------------------------

    def _eventBoost(self, horse: Horse, trackLength: int) -> str:
        jockey = self._jockeyForHorse(horse)
        dist = int(3 * (jockey.boostMultiplier if jockey else 1.0))
        horse.position = min(horse.position + dist, trackLength)
        return f"{horse.name} juoksee myötätuuleen (toisin kuin muut) ja kirii kovaa eteenpäin!"

    def _eventMotivated(self, horse: Horse) -> str:
        rounds = random.randint(1, 3)
        horse.motivatedRoundsLeft = rounds
        return f"{horse.name} on inspiroitunut. Hän juoksee vauhdikkaasti vielä {rounds} kierrosta!"

    def _eventOvertake(self, horse: Horse, trackLength: int) -> str:
        aheadHorses = [
            h for h in self.horses
            if h.status == "racing" and h.id != horse.id
            and 0 < h.position - horse.position <= 3
        ]
        if not aheadHorses:
            return None
        target = min(aheadHorses, key=lambda h: h.position)
        horse.position = min(target.position + 1, trackLength)
        return f"{horse.name} juoksee hevosen {target.name} imussa ja ohittaa hänet!"

    # ------------------------------------------------------------------
    # Negative events
    # ------------------------------------------------------------------

    def _eventDeath(self, horse: Horse) -> str:
        horse.status = "dnf"
        return f"{horse.name} kaatui ja loukkaantui niin pahasti, ettei pysty jatkamaan!"

    def _eventBackwards(self, horse: Horse) -> str:
        horse.position = max(0, horse.position - random.randint(2, 3))
        return f"{horse.name} kompastuu ja horjahtaa pahasti taaksepäin!"

    def _eventStumble(self, horse: Horse) -> str:
        horse.stumbleRoundsLeft = 1
        self._drinkBettorOfHorse(horse, 1, "hevonen kompuroi")
        return f"{horse.name} kompuroi. {horse.name} ottaa lepiä maassa!"

    def _eventSlipFall(self, horse: Horse) -> str:
        horse.position = max(0, horse.position - random.randint(2, 3))
        horse.stumbleRoundsLeft = 1
        return f"{horse.name} liukastuu, kaatuu radalle ja jää makaamaan!"

    def _eventConfused(self, horse: Horse) -> str:
        rounds = random.randint(1, 2)
        horse.confusedRoundsLeft = rounds
        self._drinkBettorOfHorse(horse, 1, "hevonen eksyi")
        return f"{horse.name} eksyy ja juoksee väärään suuntaan: {rounds} kierrosta!"

    def _eventLightning(self, horse: Horse) -> str:
        if random.randint(0, 2) == 2:
            horse.status = "dead"
            return f"Salama iskee hevoseen! {horse.name} ei selvinnyt hengissä."
        horse.speed = max(1, horse.speed - 1)
        horse.endurance = max(1, horse.endurance - 1)
        horse.luck = max(1, horse.luck - 1)
        return f"Salama viuhuu läheltä! {horse.name} selvisi hengissä mutta on järkyttynyt."

    def _eventHorseKick(self, horse: Horse) -> str:
        behind = [
            h for h in self.horses
            if h.status == "racing" and h.id != horse.id
            and h.position < horse.position
            and h.id not in self._eventedThisRound
        ]
        if not behind:
            return None
        target = random.choice(behind)
        target.stumbleRoundsLeft = 1
        target.position = max(0, target.position - random.randint(1, 2))
        return f"{horse.name} potkaisee takajalalla! {target.name} saa osuman ja kaatuu!"

    def _eventDrunkFan(self) -> str:
        pool = [h for h in self.horses if h.status == "racing" and h.id not in self._eventedThisRound]
        if not pool:
            return None
        target = random.choice(pool)
        target.stumbleRoundsLeft = 1
        self._drinkBettorOfHorse(target, 2, "juopunut katsoja kaatoi hevosen")
        return f"Juopunut katsoja juoksee radalle! {target.name} törmää häneen ja kaatuu!"

    def _shoeFallsOff(self) -> str:
        pool = [h for h in self.horses if h.status == "racing"]
        if not pool:
            return None
        target = random.choice(pool)
        target.speed = max(1, target.speed - 1)
        return f"Hevosen kenkä irtosi! {target.name} juoksee hitaammin koko kisan!"
