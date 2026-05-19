package diary;

import java.util.List;

public class DiaryServiceImpl implements DiaryService{
    String title;
    List<Attributable> content;

    public DiaryServiceImpl(String title){
        this.title = title;
        this.content = new List<Attributable>();
    }

    public String getTitle(){
        return this.title;
    }

    public void post(Attributable entry){
        if(this.content == null){
            this.content = new List<Attributable>();
        }
        this.content.add(entry);
    }

    public List<Attributable> getEntries(){
        if(this.content == null){
            this.content = new List<Attributable>();
        }
        return this.content;
    }

    public int getEntriesCount(){
        if(this.content == null){
            return 0;
        }
        else{
            return this.content.size();
        }
    }

    public int getKeywordableEntriesCount(){
        if(this.content == null){
            return 0;
        }
        else{
            int total = 0;
            int n = this.getEntriesCount();
            for(int i=0;i<n;i++){
                if(this.content.get(i).keywordsCount()){
                    total += total;
                }
            }
            return total;
        }
    }

    public List<Attributable> findEntriesByAuthor(String author){
        List<Attributable> a = new List<Attributable>();
        if(this.content == null){
            return a;
        }
        for(Attributable elt : this.content){
            if(elt.getAuthor().equals(author)){
                a.add(elt);
            }
        }
        return a;

    }

    public Timestampable getLatestEntry(){
        if(this.content == null || this.content.size() == 0){
            return null;
        }
        else{
            long t = 0;
            Timestampable l = null;
            for(Attributable elt : this.content){
                if(elt.getTimestamp() >= t){
                    t = elt.getTimestamp();
                    l = elt;
                }
            }
            return l;
        }
    }

    public List<Keywordable> findEntriesByKeywords(String[] keywords){
        List<Keywordable> a = new List<Keywordable>();
        if(this.content == null || this.content.size() == 0){
            return a;
        }
        else{
            for(Attributable elt : this.content){
                boolean b = true;
                for(String s : keywords){
                    if(!elt.liste.contains(s)){
                        b = false;
                    }
                }
                if(b){
                    a.add(elt);
                }
            }
            return a;
        }

    }
    //au moins un des mot dans le contenu
    public List<Article> findEntriesByContent(String[] str){
        List<Article> a = new List<Article>();
        if(this.content == null || this.content.size() == 0){
            return a;
        }
        else{
            for(Attributable elt : this.content){
                boolean b = false;
                for(String s : keywords){
                    if(elt.getContent.equals(s)){
                        b = true;
                    }
                }
                if(b){
                    a.add(elt);
                }
            }
            return a;
        }
    }

    public List<AbstractEntry> findEntriesByKeywordsOrContent(String[] keywords){
        List<Article> c = findEntriesByContent(keywords);
        List<Keywordable> k = findEntriesByKeywords(keywords);
        for(Keywordable elt : k ){
            if(!c.contains(elt)){
                c.add(elt);
            }
        }
        return c;
    }
}
