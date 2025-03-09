"""Tests for Turnover Percentage feature."""

import polars as pl
import pytest

from src.features.possession.P01_possessions import Possessions
from src.features.possession.P05_turnover_percentage import TurnoverPercentage
from tests.features.test_utils import validate_feature_output


class TestTurnoverPercentage:
    """Tests for the Turnover Percentage feature."""

    def test_instantiation(self) -> None:
        """Test that the feature can be instantiated correctly."""
        feature = TurnoverPercentage()
        assert feature.id == "P05"
        assert feature.name == "Turnover Percentage"
        assert feature.category == "possession"
        assert feature.description is not None

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = TurnoverPercentage()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        # Add required columns if they don't exist
        if "team_box" in mock_data_dict:
            team_box = mock_data_dict["team_box"]
            columns_to_add = []
            
            if "offensive_rebounds" not in team_box.columns:
                columns_to_add.append(pl.lit(10).alias("offensive_rebounds"))
                
            if "team_rebounds" not in team_box.columns:
                columns_to_add.append(pl.lit(5).alias("team_rebounds"))
                
            if "opponent_defensive_rebounds" not in team_box.columns:
                columns_to_add.append(pl.lit(20).alias("opponent_defensive_rebounds"))
                
            if columns_to_add:
                team_box = team_box.with_columns(columns_to_add)
                mock_data_dict["team_box"] = team_box
        
        # Create a possessions feature to pass to turnover percentage
        possessions_feature = Possessions()
        feature = TurnoverPercentage(possessions_feature=possessions_feature)
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "team_name" in result.columns
        assert "team_location" in result.columns
        assert "season" in result.columns
        assert "turnover_pct" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "turnover_pct", 
            min_val=0.0,  # Turnover percentage should be between 0 and 100
            max_val=100.0,   # Since it's expressed as a percentage
        )
        
    def test_calculation_logic(self) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case with two teams
        test_data = pl.DataFrame([
            # Team A - Game 1
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "turnovers": 15, "field_goals_attempted": 60, "free_throws_attempted": 20,
             "offensive_rebounds": 10, "team_rebounds": 5, "opponent_defensive_rebounds": 20},
            
            # Team A - Game 2
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "turnovers": 10, "field_goals_attempted": 65, "free_throws_attempted": 15,
             "offensive_rebounds": 12, "team_rebounds": 4, "opponent_defensive_rebounds": 18},
            
            # Team B - Game 1
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "turnovers": 5, "field_goals_attempted": 50, "free_throws_attempted": 10,
             "offensive_rebounds": 8, "team_rebounds": 4, "opponent_defensive_rebounds": 18},
            
            # Team B - Game 2
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "turnovers": 7, "field_goals_attempted": 55, "free_throws_attempted": 12,
             "offensive_rebounds": 9, "team_rebounds": 3, "opponent_defensive_rebounds": 19},
        ])
        
        # Create a possessions feature to pass to turnover percentage
        possessions_feature = Possessions()
        feature = TurnoverPercentage(possessions_feature=possessions_feature)
        result = feature.calculate({"team_box": test_data})
        
        # Check structure is correct
        assert "turnover_pct" in result.columns
        assert result.height == 2  # Two teams
        
        # The actual values will depend on Possessions calculation
        # Ensure Team A has a higher turnover percentage than Team B
        team_a_to_pct = result.filter(pl.col("team_id") == 1)["turnover_pct"][0]
        team_b_to_pct = result.filter(pl.col("team_id") == 2)["turnover_pct"][0]
        assert team_a_to_pct > team_b_to_pct, (
            f"Expected Team A turnover percentage ({team_a_to_pct}) to be higher than Team B ({team_b_to_pct})"
        )

    def test_handles_missing_required_columns(self, mock_team_box_data) -> None:
        """Test that the feature handles missing required columns."""
        # Add required columns if they don't exist
        columns_to_add = []
        
        if "offensive_rebounds" not in mock_team_box_data.columns:
            columns_to_add.append(pl.lit(10).alias("offensive_rebounds"))
            
        if "team_rebounds" not in mock_team_box_data.columns:
            columns_to_add.append(pl.lit(5).alias("team_rebounds"))
            
        if "opponent_defensive_rebounds" not in mock_team_box_data.columns:
            columns_to_add.append(pl.lit(20).alias("opponent_defensive_rebounds"))
            
        if columns_to_add:
            mock_team_box_data = mock_team_box_data.with_columns(columns_to_add)
        
        # Create a possessions feature to pass to turnover percentage
        possessions_feature = Possessions()
        feature = TurnoverPercentage(possessions_feature=possessions_feature)
        
        # Create a copy with missing columns
        df_missing = mock_team_box_data.drop(["turnovers"])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": df_missing})

    def test_handles_zero_possessions(self) -> None:
        """Test that the feature handles zero possessions correctly."""
        # Create a dataset with multiple games for a team, including some with potential zero possessions
        test_data = pl.DataFrame([
            # Regular games
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "turnovers": 15, "field_goals_attempted": 60, "free_throws_attempted": 20,
             "offensive_rebounds": 10, "team_rebounds": 5, "opponent_defensive_rebounds": 20},
            
            # Game with values that would lead to very low or zero possessions
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "turnovers": 0, "field_goals_attempted": 0, "free_throws_attempted": 0,
             "offensive_rebounds": 0, "team_rebounds": 0, "opponent_defensive_rebounds": 0},
        ])
        
        # Create a possessions feature to pass to turnover percentage
        possessions_feature = Possessions()
        feature = TurnoverPercentage(possessions_feature=possessions_feature)
        
        # Should handle this gracefully
        result = feature.calculate({"team_box": test_data})
        
        # The feature should still include Team A
        assert result.filter(pl.col("team_id") == 1).height == 1 