package diary;

import java.util.List;

public interface DiaryService {
    String getTitle();
    void post(Attributable entry);
    List<Attributable> getEntries();
    int getEntriesCount();
    int getKeywordableEntriesCount();
    List<Attributable> findEntriesByAuthor(String author);
    Timestampable getLatestEntry();
    List<Keywordable> findEntriesByKeywords(String[] keywords);
    List<Article> findEntriesByContent(String[] str);
    List<AbstractEntry> findEntriesByKeywordsOrContent(String[] keywords);
    
}
