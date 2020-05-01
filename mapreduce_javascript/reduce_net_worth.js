function(key, values){
	var result = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0};
	for(var i = 0; i < values.length; i++){
		for(var k = 1; k <= 5; k++){
			result[k] = result[k] + values[i][k];
		}
	}
	return result;
}