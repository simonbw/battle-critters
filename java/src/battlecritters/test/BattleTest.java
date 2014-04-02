package battlecritters.test;

import battlecritters.battle.Battle;

public class BattleTest {
	
	public static void main(String[] args) {
		Battle battle = new Battle();

		System.out.println("Initializing Battle");
		
		battle.addCritter("simon", "Husky");

		System.out.println("Running Battle");
		battle.start();
		while (!battle.isOver()) {
			battle.nextFrame();
		}

		System.out.println("Winner is: " + battle.getWinner());
	}

}
