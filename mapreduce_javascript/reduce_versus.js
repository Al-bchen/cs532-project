function(key, values){
	var result = {'with_win': 0, 'with_lose': 0, 'against_win': 0, 'against_lose': 0, 'ban_win': 0, 'ban_lose': 0};
	for(var i = 0; i < values.length; i++){
		result['with_win'] = result['with_win'] + values[i]['with_win'];
		result['with_lose'] = result['with_lose'] + values[i]['with_lose'];
		result['against_win'] = result['against_win'] + values[i]['against_win'];
		result['against_lose'] = result['against_lose'] + values[i]['against_lose'];
		result['ban_win'] = result['ban_win'] + values[i]['ban_win'];
		result['ban_lose'] = result['ban_lose'] + values[i]['ban_lose'];
	}
	return result;
}