package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class AbstractEntryTest {

	class MyEntry extends diary.AbstractEntry{
		public MyEntry(long publicationDate, String author) {
			super(publicationDate, author);
		}
	}

	@Test
	public void testSuperTypes() {
		MyEntry p = new MyEntry(1259838000, "Jean-Luc Picard");
		assertInstanceOf(p, "diary.AbstractEntry");
		assertInstanceOf(p, "diary.Attributable");
		assertInstanceOf(p, "diary.Timestampable");
	}

	@Test
	public void testGetTimestamp() {
		MyEntry p = new MyEntry(1259838000, "Jean-Luc Picard");

		long expected = 1259838000;
		long value = p.getTimestamp();
		assertEquals(expected, value);

		p = new MyEntry(1261655940, "Benjamin Sisko");

		expected = 1261655940;
		value = p.getTimestamp();
		assertEquals(expected, value);
	}

	@Test
	public void testGetAuthor() {
		MyEntry p = new MyEntry(1259838000, "Jean-Luc Picard");

		String expectedS = "Jean-Luc Picard";
		String valueS = p.getAuthor();
		assertEquals(expectedS, valueS);

		p = new MyEntry(1261655940, "Benjamin Sisko");

		expectedS = "Benjamin Sisko";
		valueS = p.getAuthor();
		assertEquals(expectedS, valueS);
	}

}
