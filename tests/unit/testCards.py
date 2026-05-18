import unittest
from core.cards import Cards

class TestCards(unittest.TestCase):


    def testStr(self):
        self.assertEqual(str(Cards("A", "Hearts")), "♥A")
        self.assertEqual(str(Cards("10", "Spades")), "♠10")

    def testValueNumbers(self):
        self.assertEqual(Cards("2", "Hearts").value(), 2)
        self.assertEqual(Cards("10", "Hearts").value(), 10)

    def testValueFaceCards(self):
        self.assertEqual(Cards("J", "Hearts").value(), 11)
        self.assertEqual(Cards("Q", "Hearts").value(), 12)
        self.assertEqual(Cards("K", "Hearts").value(), 13)
        self.assertEqual(Cards("A", "Hearts").value(), 14)

    def testFaceCardsHaveUniqueValues(self):
        self.assertGreater(Cards("J", "Hearts").value(), Cards("10", "Hearts").value())
        self.assertGreater(Cards("Q", "Hearts").value(), Cards("J", "Hearts").value())
        self.assertGreater(Cards("K", "Hearts").value(), Cards("Q", "Hearts").value())
        self.assertGreater(Cards("A", "Hearts").value(), Cards("K", "Hearts").value())

    def testIsRed(self):
        self.assertTrue(Cards("A", "Hearts").isRed())
        self.assertTrue(Cards("A", "Diamonds").isRed())
        self.assertFalse(Cards("A", "Clubs").isRed())
        self.assertFalse(Cards("A", "Spades").isRed())

    def testIsBlack(self):
        self.assertTrue(Cards("A", "Clubs").isBlack())
        self.assertTrue(Cards("A", "Spades").isBlack())
        self.assertFalse(Cards("A", "Hearts").isBlack())

    def testIsFaceCard(self):
        self.assertTrue(Cards("J", "Hearts").isFaceCard())
        self.assertTrue(Cards("Q", "Hearts").isFaceCard())
        self.assertTrue(Cards("K", "Hearts").isFaceCard())
        self.assertFalse(Cards("A", "Hearts").isFaceCard())
        self.assertFalse(Cards("10", "Hearts").isFaceCard())


if __name__ == "__main__":
    unittest.main()