package battlecritters;

import battlecritters.battle.Battle;

/**
 * The objects returned from the GatewayServer to python using py4j.
 */
public class EntryPoint {

	public EntryPoint() {
	}

	/**
	 * Creates a new battle object.
	 * 
	 * @return new battle
	 */
	public Battle createBattle(int length, int width, int height) {
		System.out.println("Java creating new battle");
		return new Battle(length, width, height);
	}
}