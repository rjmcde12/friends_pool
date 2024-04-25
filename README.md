# friends_pool

Website built to track a custom March Madness pool designed by a friend. The game results were updated in real-time via and NCAA scoreboard api. The website has since been discontinued.

Rules of the Pool:
Number of players: 
8 (but 4, 8, 16 all would work)

Team selection: 
Create random order of players and conduct a snake draft until all teams are selected (first round: 1-8, second round 8-1, etc) This should be done once the playin games are completed (or allow the players to select both teams of the play-in games as one and they will be assigned the winner)

Point System:
The points are determined by the round x team seed. 
Opening Round - 1
Second Round - 2
Sweet 16 - 3
Elite 8 - 4
Final 4 - 5
Championship Game - 6

The winning team is awarded points by multiplying their seed by the round. The points for each round are aggregated together. Each player's score is the aggregate of all their teams' total scores.
For Example:
UConn is a 1 seed. A first round win is worth 1, second round 2, etc. If UConn wins the tournament, they will earn 21 total points.
Gonzaga is a 5 seed. A first round win is worth 5, second round 10, Sweet 16 15, etc. If Gonzaga reaches the Elite 8 (wins the Sweet 16 then loses in the Elite 8) they will earn 30 total points.

As you can see, while normally a heavy favorite like UConn is valuable, they only max out at 21 total potential points. Where as a lower seed can eclipse that with just a few wins. So the calculation for the most valuable teams is more complex.

The Max Points column factors in that some teams for one player may face each other earlier in the tournament. In that case, it will take the higher valued team when calculating the max points.
