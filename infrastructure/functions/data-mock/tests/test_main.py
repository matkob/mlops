import mock_data as script


class TestProjectContext:
    def test_that_mock_data_returns_correct_columns(self) -> None:
        df = script.mock_data(10)

        levels = []
        for i in range(5):
            levels.append(f"asks_{i}_price")
            levels.append(f"asks_{i}_amount")
            levels.append(f"bids_{i}_price")
            levels.append(f"bids_{i}_amount")

        expected_columns = [
            "exchange",
            "symbol",
            "timestamp",
            "local_timestamp",
        ] + levels

        assert len(df.columns) == 24
        assert df.columns.to_list() == expected_columns

    def test_that_mock_data_returns_correct_length(self) -> None:
        df = script.mock_data(10)

        assert len(df) == 10

    def test_that_mock_data_returns_correct_exchange(self) -> None:
        df = script.mock_data(10)

        assert (df["exchange"] == "binance").all()

    def test_that_mock_data_returns_correct_symbol(self) -> None:
        df = script.mock_data(10)

        assert (df["symbol"] == "BTCUSDT").all()
