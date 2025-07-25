from unittest.mock import MagicMock

class ProductionClass:
    def method(self):
        self.something(1, 2, 3)
    def something(self, a, b, c):
        pass



def main():
    real = ProductionClass()
    real.something = MagicMock()
    real.method()
    real.something.assert_called_once_with(1, 2, 4)

if __name__ == "__main__":
    main()