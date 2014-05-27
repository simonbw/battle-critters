public class Husky extends Critter {

	// Create a new Husky
	public Husky() {
		super();
	}

	public Action getMove(CritterInfo info) {
		// 
		Neighbor left = info.getLeft();		
		Neighbor right = info.getRight();		
		Neighbor front = info.getFront();		
		Neighbor back = info.getBack();

		if (info.getFront() == OTHER) {
			return INFECT;
		}

		// check if in a group
		if (left == SAME || right == SAME || front == SAME || back == SAME) {
			if (left == OTHER) {
				return LEFT;
			} else if (right == OTHER) {
				return RIGHT;
			} else if ((left == WALL || left == SAME) && (right == WALL || right == SAME)) {
				return INFECT;
			} else if (left == WALL || left == SAME) {
				return RIGHT;
			} else if (right == WALL || right == SAME) {
				return LEFT;
			} else {
				return (Math.random() > 0.5) ? LEFT : RIGHT;
			}
		} else {
			if (left == OTHER) {
				return LEFT;
			} else if (front == EMPTY) {
				return HOP;
			} else {
				if (left == WALL) {
					return RIGHT;
				} else if (right == WALL) {
					return LEFT;
				}
			}
		}

		return LEFT;
	}
}
