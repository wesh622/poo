package diary;

import org.junit.jupiter.api.Test;

import diary.Timestampable;

import static org.junit.jupiter.api.ReflectionAssertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertNull;

import java.util.List;

public class DiaryServiceImplTest {

	@Test
	public void testSuperTypes() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");
		assertInstanceOf(b, "diary.DiaryService");
	}

	@Test
	public void testGetTitle() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");
		String expectedS = "Star trek blog";
		String valueS = b.getTitle();
		assertEquals(expectedS, valueS);

		b = new diary.DiaryServiceImpl("Another Galaxy blog");
		expectedS = "Another Galaxy blog";
		valueS = b.getTitle();
		assertEquals(expectedS, valueS);
	}
	
	@Test
	public void testGetPublishableCountAndPost() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");
		assertEquals(0, b.getEntriesCount());

		diary.Article aMessage = new diary.Article(1259838000, "Jean-Luc Picard", "Space the final frontier");
		diary.Article anotherMessage = new diary.Article(1259838000, "Quark", "Ferengi rules");

		b.post(aMessage);
		assertEquals(1, b.getEntriesCount());
		assertTrue(b.getEntries().contains(aMessage), "blog should contains my posted message");

		b.post(anotherMessage);
		assertEquals(2, b.getEntriesCount());
		assertTrue(b.getEntries().contains(anotherMessage), "blog should contains my second posted message");
		assertTrue(b.getEntries().contains(aMessage), "blog should contains my posted message");
	}

	@Test
	public void testGetTaggableItemsCount() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");
		assertEquals(0, b.getKeywordableEntriesCount());

		diary.Photo aPicture = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		diary.Photo anotherPicture = new diary.Photo(1359738000, "Jean-Luc Picard", "http://www.startrek.com/img/banner.png", "Captain Photo");
		diary.Article aMessage = new diary.Article(1259838000, "Jean-Luc Picard", "Space the final frontier");
		diary.Article anotherMessage = new diary.Article(1259838000, "Quark", "Ferengi rules");
		diary.Video aVideo = new diary.Video(1259838000, "Quark", "http://www.startrek.com/vids/trailer.avi", "Trailer", 180);

		b.post(aPicture);
		assertEquals(1, b.getKeywordableEntriesCount());
		b.post(aMessage);
		assertEquals(1, b.getKeywordableEntriesCount());
		b.post(anotherPicture);
		b.post(anotherMessage);
		assertEquals(2, b.getKeywordableEntriesCount());	
		b.post(aVideo);
		assertEquals(3, b.getKeywordableEntriesCount());	
	}
	
	@Test
	public void testFindItemsByAuthor() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");

		diary.Photo aPicture = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		diary.Photo anotherPicture = new diary.Photo(1359738000, "Quark", "http://www.startrek.com/img/banner.png", "Captain Photo");
		diary.Article aMessage = new diary.Article(1259838000, "Jean-Luc Picard", "Space the final frontier");

		List<Attributable> res = b.findEntriesByAuthor("Jean-Luc Picard");
		assertTrue(res != null, "findItemsByAuthor() should never return a null reference");
		assertEquals(0, res.size());

		b.post(aPicture);
		b.post(anotherPicture);
		b.post(aMessage);
		res = b.findEntriesByAuthor("Jean-Luc Picard");
		assertEquals(2, res.size());
		assertTrue(res.contains(aPicture), "findItemsByAuthor() did not find this picture");
		assertTrue(! res.contains(anotherPicture), "findItemsByAuthor() should not find this picture");
		assertTrue(res.contains(aMessage), "findItemsByAuthor() did not find this message");
		res = b.findEntriesByAuthor("Quark");
		assertEquals(1, res.size());
		assertTrue(res.contains(anotherPicture), "findItemsByAuthor() did not find this picture");
	}
	
	@Test
	public void testGetLatestItem() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");

		diary.Photo aPicture = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		diary.Photo anotherPicture = new diary.Photo(1359738000, "Quark", "http://www.startrek.com/img/banner.png", "Captain Photo");
		diary.Article aMessage = new diary.Article(1259837000, "Jean-Luc Picard", "Space the final frontier");

		assertNull(b.getLatestEntry());
		
		b.post(aPicture);
		Timestampable expected = aPicture;
		Timestampable res = b.getLatestEntry();
		assertEquals(expected, res);
		
		b.post(aMessage);
		expected = aPicture;
		res = b.getLatestEntry();
		assertEquals(expected, res);
		
		b.post(anotherPicture);
		expected = anotherPicture;
		res = b.getLatestEntry();
		assertEquals(expected, res);
	}

	@Test
	public void testFindItemsByTags() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");

		diary.Photo aPicture = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		diary.Photo anotherPicture = new diary.Photo(1359738000, "Quark", "http://www.startrek.com/img/banner.png", "Captain Photo");
		diary.Article aMessage = new diary.Article(1259837000, "Jean-Luc Picard", "Is there any starship near this place?");
		diary.Video aVideo = new diary.Video(1259838000, "Quark", "http://www.startrek.com/vids/trailer.avi", "Trailer", 180);

		List<Keywordable> res = b.findEntriesByKeywords(new String[] { "trekkies"});
		assertTrue(res != null, "findItemsByTags() should never return a null reference");
		assertEquals(0, res.size());

		b.post(aPicture);
		res = b.findEntriesByKeywords(new String[] { "trekkies"});
		assertEquals(0, res.size());
		aPicture.addKeyword("trekkies");
		res = b.findEntriesByKeywords(new String[] { "trekkies"});
		assertEquals(1, res.size());
		assertTrue(res.contains(aPicture), "findItemsByTags() did not find the tagged picture");
		
		b.post(anotherPicture);
		b.post(aVideo);
		b.post(aMessage);
		res = b.findEntriesByKeywords(new String[] { "trekkies"});
		assertEquals(1, res.size());
		assertTrue(res.contains(aPicture), "findItemsByTags() did not find the tagged picture");

		anotherPicture.addKeyword("space");
		anotherPicture.addKeyword("starship");
		res = b.findEntriesByKeywords(new String[] { "starship"});
		assertEquals(1, res.size());
		assertTrue(res.contains(anotherPicture), "findItemsByTags() did not find the tagged picture");

		aVideo.addKeyword("starship");
		res = b.findEntriesByKeywords(new String[] { "starship"});
		assertEquals(2, res.size());
		assertTrue(res.contains(anotherPicture), "findItemsByTags() did not find the tagged picture");
		assertTrue(res.contains(aVideo), "findItemsByTags() did not find the tagged video");

		anotherPicture.removeKeyword("starship");
		res = b.findEntriesByKeywords(new String[] { "starship"});
		assertEquals(1, res.size());
		assertTrue(res.contains(aVideo), "findItemsByTags() did not find the tagged video");	
	}
	
	@Test
	public void testFindItemsByContent() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");

		List<Article> res = b.findEntriesByContent(new String[] { "trekkies"});
		assertTrue(res != null, "findItemsByContent() should never return a null reference");
		assertEquals(0, res.size());
		
		diary.Photo aPicture = new diary.Photo(1259838000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		diary.Article aMessage = new diary.Article(1259837000, "Jean-Luc Picard", "Is there any starship near this place?");
		diary.Article anotherMessage = new diary.Article(1259836000, "Jean-Luc Picard", "The final frontier");
		diary.Article anotherMessage2 = new diary.Article(1259838000, "Jean-Luc Picard", "There is no place like home");

		b.post(aMessage);		
		res = b.findEntriesByContent(new String[] { "trekkies"});
		assertEquals(0, res.size());
		res = b.findEntriesByContent(new String[] { "starship"});
		assertEquals(1, res.size());
		assertTrue(res.contains(aMessage), "findItemsByContent() did not find the message matching the search criteria");
		res = b.findEntriesByContent(new String[] { "place"});
		assertEquals(1, res.size());
		assertTrue(res.contains(aMessage), "findItemsByContent() did not find the message matching the search criteria");
		
		aPicture.addKeyword("place");
		b.post(aPicture);
		res = b.findEntriesByContent(new String[] { "place"});
		assertEquals(1, res.size());
		assertTrue(res.contains(aMessage), "findItemsByContent() did not find the message matching the search criteria");

		b.post(anotherMessage);
		b.post(anotherMessage2);
		res = b.findEntriesByContent(new String[] { "place"});
		assertEquals(2, res.size());
		assertTrue(res.contains(aMessage), "findItemsByContent() did not find the message matching the search criteria");
		assertTrue(res.contains(anotherMessage2), "findItemsByContent() did not find the message matching the search criteria");
	}
	
	@Test
	public void testFindItemsByTagsOrContent() {
		diary.DiaryServiceImpl b = new diary.DiaryServiceImpl("Star trek blog");
		
		List<AbstractEntry> res = b.findEntriesByKeywordsOrContent(new String[] { "trekkies"});
		assertTrue(res != null, "findItemsByTagsOrContent() should never return a null reference");
		assertEquals(0, res.size());
		
		diary.Photo aPicture = new diary.Photo(125989000, "Jean-Luc Picard", "http://www.startrek.com/img/logo.png", "Captain Photo");
		diary.Photo anotherPicture = new diary.Photo(1359738000, "Quark", "http://www.startrek.com/img/banner.png", "Captain Photo");
		diary.Article aMessage = new diary.Article(1259837000, "Jean-Luc Picard", "Is there any starship near this place?");
		diary.Video aVideo = new diary.Video(1259835000, "Quark", "http://www.startrek.com/vids/trailer.avi", "Trailer", 180);

		b.post(aPicture);
		b.post(anotherPicture);		
		anotherPicture.addKeyword("space");
		anotherPicture.addKeyword("starship");
		b.post(aMessage);
		aVideo.addKeyword("starship");		
		b.post(aVideo);		
		
		res = b.findEntriesByKeywordsOrContent(new String[] { "space", "starship"  });
		assertEquals(1, res.size());
		assertTrue(res.contains(anotherPicture), "findItemsByTagsOrContent() did not find the message matching the search criteria");
	}
	
}
