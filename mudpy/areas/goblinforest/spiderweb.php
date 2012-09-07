<?php
use Phud\Room\Room,
	Phud\Room\Area,
	Phud\Actors\Mob;

$area_den = new Area(['alias' => 'spiderden']);
$id = 'goblinforestspiderweb';

$spider = [
	'alias' => 'a small green spider',
	'nouns' => 'green spider',
	'long' => 'An unintimidating little green spider scurries across your path.',
];

new Room([
	'id' => $id.'0',
	'short' => 'Climbing a spider web',
	'long' => 'A monstrous web has engulfed the trees around it. The main arterials are just strong enough to support your weight.',
	'area' => $area_den,
	'down' => 'goblinforest3',
	'actors' => [
		new Mob($spider)
	]
]);
?>
