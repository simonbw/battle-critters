package battlecritters.critterloader;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

/**
 * Loads classes dynamically from their .class files. Only loads the first class dynamically. Following classes are
 * loaded with the fallback loader given.
 */
public class CritterClassLoader extends ClassLoader {

	boolean active;
	/**
	 * The loader to use when this one fails.
	 */
	private ClassLoader fallback;

	/**
	 * Create a new Reloader using the system class loader as a fallback.
	 */
	public CritterClassLoader() {
		this(ClassLoader.getSystemClassLoader());
	}

	/**
	 * Create a new reloader with a custom fallback loader.
	 * 
	 * @param fallback
	 *            custom fallback loader to use.
	 */
	public CritterClassLoader(ClassLoader fallback) {
		super();
		this.fallback = fallback;
		active = true;
	}

	@Override
	public Class<?> loadClass(String s) {
		return findClass(s);
	}

	@Override
	public Class<?> findClass(String s) {
		if (active && s.startsWith("battlecritters.critters")) {
			try {
				byte[] bytes = loadClassData(s);
				return defineClass(s, bytes, 0, bytes.length);
			} catch (IOException ioe) {
				try {
					System.out.println("Using fallback loader");
					return fallback.loadClass(s);
				} catch (ClassNotFoundException ignore) {
				}
				ioe.printStackTrace(System.out);
				return null;
			}
		} else {
			try {
				return fallback.loadClass(s);
			} catch (ClassNotFoundException e) {
				e.printStackTrace();
				return null;
			}
		}
	}

	/**
	 * Load class data based on the class name.
	 * 
	 * @param className
	 * @return class data
	 * @throws IOException
	 */
	private byte[] loadClassData(String className) throws IOException {
		File f = new File("java\\bin\\" + className.replaceAll("\\.", "/") + ".class");
		System.out.println(f.getAbsolutePath());
		int size = (int) f.length();
		byte buff[] = new byte[size];
		FileInputStream fis = new FileInputStream(f);
		DataInputStream dis = new DataInputStream(fis);
		dis.readFully(buff);
		dis.close();
		return buff;
	}

	public String toString() {
		return "<Custom (Re)Loader>";
	}
}
