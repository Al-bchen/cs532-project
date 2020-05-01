function(){
	if(this.picks_bans != null){
		for(var i = 0; i < this.picks_bans.length; i++){
			if(this.picks_bans[i].hero_id == {HERO_ID} && this.picks_bans[i].is_pick == true){
				// is target hero and is picked
				for(var k = 0; k < this.picks_bans.length; k++){
					if(i != k){
						var against_win = 0;
						var against_lose = 0;
						var with_win = 0;
						var with_lose = 0;
						var ban_win = 0;
						var ban_lose = 0;
						if(this.picks_bans[k].is_pick == true){
							// pick
							if(this.picks_bans[i].team == this.picks_bans[k].team){
								// same team -> teammate
								if((this.picks_bans[i].team == 0 && this.radiant_win == true) ||
								(this.picks_bans[i].team == 1 && this.radiant_win == false)){
									// with win
									with_win = 1;
								}
								else{
									// with lose
									with_lose = 1;
								}
							}
							if(this.picks_bans[i].team != this.picks_bans[k].team){
								// different team -> opponent
								if((this.picks_bans[i].team == 0 && this.radiant_win == true) ||
								(this.picks_bans[i].team == 1 && this.radiant_win == false)){
									// against win
									against_win = 1;
								}
								else{
									// against lose
									against_lose = 1;
								}
							}
						}
						if(this.picks_bans[k].is_pick == false){
							// ban
							if(true){
								// no matter opponent or teammate
								if((this.picks_bans[i].team == 0 && this.radiant_win == true) ||
								(this.picks_bans[i].team == 1 && this.radiant_win == false)){
									// ban win
									ban_win = 1;
								}
								else{
									// ban lose
									ban_lose = 1;
								}
							}
						}
						emit(this.picks_bans[k].hero_id, {'with_win': with_win, 'with_lose': with_lose, 'against_win': against_win, 'against_lose': against_lose, 'ban_win': ban_win, 'ban_lose': ban_lose})
					}
				}
				return;
			}
		}
	}
	else{
		// Do nothing
		return;
	}
}