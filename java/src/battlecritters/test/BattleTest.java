package battlecritters.test;

import battlecritters.battle.Battle;

public class BattleTest {
	
	public static void main(String[] args) {
		Battle battle = new Battle();

		battle.addCritter("simon", "Husky");
		battle.start();
		while (!battle.isOver()) {
			battle.nextFrame();
		}
		System.out.println(battle.getWinner());
	}

}
