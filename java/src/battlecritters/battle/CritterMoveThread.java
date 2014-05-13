package battlecritters.battle;

public class CritterMoveThread extends Thread {

	public Critter.Action move;

	private Critter critter;

	private CritterInfo info;

	public CritterMoveThread(Critter critter, CritterInfo info) {
		super();
		this.critter = critter;
		this.info = info;
		move = Critter.Action.HOP;
	}

	@Override
	public void run() {
		// System.out.println("CritterMoveThread running");
		try {
			move = critter.getMove(info);
		} catch (Exception e) {
			System.out.println("Error getting move");
		}
	}
}