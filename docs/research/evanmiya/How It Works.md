## Overview

Welcome to EvanMiya College Basketball Analytics, where you can find team ratings, player ratings, lineup metrics, transfer portal rankings, game predictions, and much more. The main objective of our work is to assess college basketball team and player strength. We have created an advanced statistical metric, **Bayesian Performance Rating (BPR)**, which quantifies how effective a team or player is, using advanced box-score metrics, play-by-play data, and historical information. This metric is predictive in nature, which means that each rating is fine-tuned to predict performance in future games.

There are several pages of analysis (plus several more that appear when appropriate):

- **Team Ratings**: We assess the strength of each team by calculating offensive and defensive ratings that reflect the team’s offensive and defensive efficiency, while accounting for other factors, such as game pace and opponent strength. Read more about the [new team ratings methodology here](https://blog.evanmiya.com/p/introducing-relative-ratings-and).
- **Player Ratings**: We quantify the value of each player to his team on both offense and defense. A player’s ratings incorporate his individual efficiency statistics, along with his impact on the court for his team, which is assessed by looking at how successful his team was in every possession he played. These ratings account for the strength of all other players on the floor with that player in each of his possessions that he played.
- **Player Projections**: This tool takes each player’s game-by-game history and quantifies their skill level in every major statistical category (three-point shooting, rebounding, steals, etc.) by predicting how well they will perform in that stat moving forward. These projections adjust for important contextual variables across their career, including opponent strength, offensive usage, expected year-by-year improvement, and recent form. You can read more about the tool [here](https://blog.evanmiya.com/p/new-tool-player-skill-projections).
- **Lineup Metrics and Projections**: We rate all two, three, four, and five man lineups across all of Division 1 basketball, adjusted for the strength of opposing players faced by each lineup. We also predict lineup performance for every 5-man lineup in the country, grading strengths and weaknesses for each based on player personnel. You can read more about the tool [here](https://blog.evanmiya.com/p/lineup-data-just-got-a-whole-lot).
- **Transfer Portal**: This tool provides rankings for every player in the transfer portal, updated daily during the portal season. We also have transfer class rankings and advanced transfer scouting reports.
- **Team Breakdown Tool**: This tool provides a more detailed look into player and lineup metrics for each team.
- **Keys to Victory**: We provide automated keys to victory for every team and provide tables and visualizations for exploring how different metrics impact a team’s performances.
- **Game Predictions**: Our advanced statistical model predicts the results of every game and provides comparisons to Vegas lines as well as “Best Bets”. You can read more about the [Game Predictions model here](https://blog.evanmiya.com/p/evanmiyacom-game-predictions-strategy). We also provide Matchup Previews for upcoming games, which includes predicted score calculations, team comparisons, roster breakdowns, and injury reports.

Now for some more detail into how we get these numbers:

**Collecting Data**

We have box score data available for every game played in the each college basketball season, along with play-by-play data, which includes substitutions. The possession by possession data is the main component used to drive our analysis.

**Adjusting for the strength of opposition**

At both a team and player level, our metrics adjust for the strength of opposition for every possession played. For players, this includes an adjustment for the individual level of every single opposing player on the floor for a possession, along with the strength of teammates as well.

**Tempo free statistics**

All of our metrics adjust for the pace of play in a game by looking at efficiency on a per-possession basis.

## Bayesian Performance Rating

We have created an advanced statistical metric, **Bayesian Performance Rating (BPR)**, which quantifies how effective a player is, using advanced box-score metrics, play-by-play data, and historical information (for the basketball metric nerds, this is a highly technical version of an adjusted plus-minus). This metric is predictive in nature, which means that each rating is fine-tuned to predict performance in future games.

BPR quantifies the value of each player to his team on both offense and defense. A player’s ratings incorporate his individual efficiency statistics, along with his impact on the court for his team, which is assessed by looking at how successful his team was in every possession he played. These ratings account for the strength of all other players on the floor with that player in each of his possessions that he played. Each player has an Offensive BPR and a Defensive BPR, which are added together to make the player’s overall BPR. Very good players will have higher positive offensive and defensive ratings, with the average D1 player having an Offensive BPR and Defensive BPR of 0. Like other adjusted plus-minus metrics, BPR values are interpreted as the expected points per 100 possessions better than a D1 average player while on the floor.

The BPR statistical model is trained on data going back to 2011, making it the most fine-tuned player evaluation metric in college basketball.

#### First Stage: Historical Stats

The first stage in forming a player’s rating is in the form of a projection for the season, based on that player’s statistics and metrics in previous seasons, along with other predictive information, such as recruiting ratings. Though the historical information does not influence BPR much by the end of a season, it is incredibly useful as it allows for Bayesian Performance Rating to be effective in assessing a player’s impact, even when he hasn’t played much (or at all) in the current season.

#### Second Stage: Individual Stats

The second stage in forming a player’s rating is his Box Bayesian Performance Rating (Box BPR), which is an estimate of a player’s impact on both ends of the court, using only his individual box score statistics. Box BPR, which is essentially our own version of a Box-Plus-Minus, can give us a good initial estimate of a player’s statistical worth. Though we don’t want to use Box BPR as the final representation of a player’s effectiveness, we can still use the metric to help guide our final ratings by using it as a starting point.

#### Third Stage: Play-by-Play Impact

The third stage looks at every possession a player played, attempting to quantify his value to his team by looking at how efficiently his team performed on offense and defense for those plays. In addition, we also adjust for the strength of his teammates on the court with him, along with the strength of opposing players for each possession he was on the court. Essentially, our model finds the offensive and defensive rating for each player that can best explain the results from every possession that occurred from the season, for all players. The Box BPR is the starting point for a given player, but the rating will move up if he had more of an impact than his individual stats suggested, or vice versa. In some cases, the final BPR will be very close to the Box BPR, and in other cases they will be very different. Players who look really good on the stat sheet often evaluate well, but equally so, guys who control the game beyond what their stats convey will also be credited accordingly.

## Team Ratings

We have a new team strength model, called “Relative Ratings”, that ranks teams based on how they would perform head-to-head against other teams of similar quality. Each team has a true offensive and a true defensive rating that best explains all of the real game results that are observed from the season, while also incorporating other predictive statistics, such as team historical information. Additionally, we account for matchup-specific variables, such as how well a team plays against elite competition versus weaker competition, and whether a team performs better in fast paced or slow tempo games. Read more here [at the EvanMiya.com blog](https://blog.evanmiya.com/).

## How To Use BPR

The purpose of Bayesian Performance Rating is to identify the players who are having the biggest impact on the offensive and defensive side of the ball. BPR cannot provide everything that an eye-test can, but is a very helpful tool to either confirm what we thought was true of a player, or provide insight into trends we could have missed. By sorting a roster by BPR, the order will often be close to what you might have expected after watching the games. However, it is helpful to note which players evaluate much higher or lower than we might have expected, and to try to explain why. When I am trying to understand why a player has the rating that he does, I look at three stats, in order, which are all listed in the Team Breakdown Tool - Players page for each player.

1. Box Plus Minus
    - Box Offensive BPR and Box Defensive BPR sum up a player’s individual efficiency stats into one number that estimates effectiveness on that side of the court. Since this serves as the starting point for the final BPR calculation, it’s the first place I look if I am trying to explain a particular player’s evaluation. If a player’s Box BPR is higher than expected, it might be because he was more efficient in some statistical category on a per possession basis than I realized.   
        
2. Adjusted Team Efficiency
    - The metrics in this category tell how many points per 100 possessions a team scored or conceded with that player on the floor. This does a calculation of efficiency on both sides of the court on a per possession basis, and adjusts for the strength of opposition players faced by that lineup. Often, a player who has a higher BPR on his team also has one of the higher Team Efficiency Margins, since this is a huge component to the calculation of the rating.
3. Average Opponent BPR
    - This shows the average rating of the individual opponents faced by a player when he was on the floor. If a player has a higher Avg Opp BPR than other teammates, this indicates that he had to play against better players when he was on the floor, and his BPR will be adjusted higher accordingly.

Additionally, we have also included each player’s estimated position and offensive role in the Team Table, which is based on individual stats and team contributions. An estimated position of 1 corresponds to being a point guard, and a 5 corresponds to being a center. An estimated offensive role of 1 corresponds to being the “creator” in the offense, and a 5 corresponds to being the “receiver”. These can be helpful see if a player’s statistical contribution was similar to how they were envisioned to be helping the team. Bayesian Performance Rating is not biased based on position or offensive role.