import unittest
from core.cards import Card
from tests.testUtils import SilentTest

class TestCard(SilentTest):

    def testStr(self):
        self.assertEqual(str(Card("A", "Hearts")), "♥A")
        self.assertEqual(str(Card("10", "Spades")), "♠10")

    def testValueNumbers(self):
        self.assertEqual(Card("2", "Hearts").value(), 2)
        self.assertEqual(Card("10", "Hearts").value(), 10)

    def testValueFaceCard(self):
        self.assertEqual(Card("J", "Hearts").value(), 11)
        self.assertEqual(Card("Q", "Hearts").value(), 12)
        self.assertEqual(Card("K", "Hearts").value(), 13)
        self.assertEqual(Card("A", "Hearts").value(), 14)

    def testFaceCardHaveUniqueValues(self):
        self.assertGreater(Card("J", "Hearts").value(), Card("10", "Hearts").value())
        self.assertGreater(Card("Q", "Hearts").value(), Card("J", "Hearts").value())
        self.assertGreater(Card("K", "Hearts").value(), Card("Q", "Hearts").value())
        self.assertGreater(Card("A", "Hearts").value(), Card("K", "Hearts").value())

    def testIsRed(self):
        self.assertTrue(Card("A", "Hearts").isRed())
        self.assertTrue(Card("A", "Diamonds").isRed())
        self.assertFalse(Card("A", "Clubs").isRed())
        self.assertFalse(Card("A", "Spades").isRed())

    def testIsBlack(self):
        self.assertTrue(Card("A", "Clubs").isBlack())
        self.assertTrue(Card("A", "Spades").isBlack())
        self.assertFalse(Card("A", "Hearts").isBlack())

    def testIsFaceCard(self):
        self.assertTrue(Card("J", "Hearts").isFaceCard())
        self.assertTrue(Card("Q", "Hearts").isFaceCard())
        self.assertTrue(Card("K", "Hearts").isFaceCard())
        self.assertFalse(Card("A", "Hearts").isFaceCard())
        self.assertFalse(Card("10", "Hearts").isFaceCard())


if __name__ == "__main__":
    unittest.main()