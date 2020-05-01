function(){
	if(this.picks_bans != null){
		for(var i = 0; i < this.players.length; i++){
			if(this.players[i].hero_id == {HERO_ID}){
				// is target hero and is picked by player
				var count = 0;
				var team = 0;
				if(this.players[i].player_slot >= 128)
					team = 1;
				for(var k = 0; k < this.players.length; k++){
					if(i != k){
						var team2 = 0;
						if(this.players[k].player_slot >= 128)
							team2 = 1;
						if(team == team2){
							if(this.players[k].total_gold > this.players[i].total_gold){
								count += 1;
							}
						}
					}
				}
				var result = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0};
				result[count+1] = result[count+1] + 1;
				emit(this.leagueid, result)
				return;
			}
		}
	}
	else{
		// Do nothing
		return;
	}
}