package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class AbstractMediaTest {

	class MyItem extends diary.AbstractMedia{

		public MyItem(long publicationDate, String author) {
			super(publicationDate, author);
		}
	
	}

	@Test
	public void testSuperTypes() {
		MyItem p = new MyItem(1259838000, "Jean-Luc Picard");
		assertInstanceOf(p, "diary.AbstractMedia");
		assertInstanceOf(p, "diary.Attributable");
		assertInstanceOf(p, "diary.Keywordable");
	}

	@Test
	public void testGetTimestamp() {
		MyItem p = new MyItem(1259838000, "Jean-Luc Picard");

		long expected = 1259838000;
		long value = p.getTimestamp();
		assertEquals(expected, value);

		p = new MyItem(1261655940, "Benjamin Sisko");

		expected = 1261655940;
		value = p.getTimestamp();
		assertEquals(expected, value);
	}

	@Test
	public void testGetAuthor() {
		MyItem p = new MyItem(1259838000, "Jean-Luc Picard");

		String expectedS = "Jean-Luc Picard";
		String valueS = p.getAuthor();
		assertEquals(expectedS, valueS);

		p = new MyItem(1261655940, "Benjamin Sisko");

		expectedS = "Benjamin Sisko";
		valueS = p.getAuthor();
		assertEquals(expectedS, valueS);
	}
	
	@Test
	public void testAddAndGetKeyword() {
		MyItem p = new MyItem(1259838000, "Jean-Luc Picard");
		
		assertEquals(0, p.keywordsCount());
		p.addKeyword("trekkies");
		assertEquals(1, p.keywordsCount());
		assertTrue(p.getKeywords().contains("trekkies"), "tag 'trekkies' is missing on the tagged item");
		
		p.addKeyword("trekkies");
		assertEquals(1, p.keywordsCount());  // "an item might not be tagged twice with the same tag"
		p.addKeyword("starship");
		assertEquals(2, p.keywordsCount());		
		assertTrue(p.getKeywords().contains("trekkies"), "tag 'trekkies' is missing on the tagged item");
		assertTrue(p.getKeywords().contains("starship"), "tag 'starship' is missing on the tagged item");
		
		p.addKeyword(null);
		assertEquals(2, p.keywordsCount());				
	}

	@Test
	public void testRemoveAndGetKeyword() {
		MyItem p = new MyItem(1259838000, "Jean-Luc Picard");
		
		p.removeKeyword(null);
		assertEquals(0, p.keywordsCount());				

		p.addKeyword("trekkies");
		p.removeKeyword("trekkies");
		assertEquals(0, p.keywordsCount());
		assertTrue(p.getKeywords().contains("trekkies") == false, "tag 'trekkies' should have been removed on the tagged item");
		
		p.addKeyword("enterprise");
		p.addKeyword("trekkies");
		p.addKeyword("starship");
		p.removeKeyword(null);
		assertEquals(3, p.keywordsCount());				
		
		p.removeKeyword("trekkies");
		assertEquals(2, p.keywordsCount());		
		assertTrue(p.getKeywords().contains("trekkies") == false, "tag 'trekkies' should have been removed on the tagged item");
		assertTrue(p.getKeywords().contains("starship"), "tag 'starship' is missing on the tagged item");
		assertTrue(p.getKeywords().contains("enterprise"), "tag 'enterprise' is missing on the tagged item");
	}
}
