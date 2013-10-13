package battlecritters.battle;

/**
 * 
 */
public interface CritterInfo {
	public Critter.Neighbor getFront();

	public Critter.Neighbor getBack();

	public Critter.Neighbor getLeft();

	public Critter.Neighbor getRight();

	public Critter.Direction getDirection();

	public int getInfectCount();
}