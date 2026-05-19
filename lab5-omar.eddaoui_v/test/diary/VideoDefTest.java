package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredConstructor;

import static org.junit.jupiter.api.ReflectionAssertions.assertInstanceOf;

public class VideoDefTest {
	
	public void testDeclaredMethods() {		
		assertDeclaredMethod("diary.Video", "getURL", new String[] { }, "missing method getURL() in class Video");
		assertDeclaredMethodWithReturnType("diary.Video", "getURL", new String[] { }, "java.lang.String", "missing method getURL() in class Video");
	}

	@Test
	public void testDeclaredConstructors() {		
		assertDeclaredConstructor("diary.Video", new String[] { "long", "java.lang.String", "java.lang.String", "java.lang.String", "int" }, "missing constructor Video(long, String, String, String, int) in class Video");
	}
	
	@Test
	public void testSuperTypes() {
		diary.Video v = new diary.Video(1259838000, "Jean-Luc Picard", "http://www.startrek.com/vids/trailer.mpg", "Trailer", 180);
		assertInstanceOf(v, "diary.AbstractMedia");
		assertInstanceOf(v, "diary.Attributable");
		assertInstanceOf(v, "diary.Timestampable");
		assertInstanceOf(v, "diary.Keywordable");
	}


}
