package diary;

import java.util.ArrayList;
import java.util.List;

public class DiaryServiceImpl implements DiaryService{
    String title;
    ArrayList<Attributable> content;

    public DiaryServiceImpl(String title){
        this.title = title;
        this.content = new ArrayList<Attributable>();
    }

    public String getTitle(){
        return this.title;
    }

    public void post(Attributable entry){
        if(this.content == null){
            this.content = new ArrayList<Attributable>();
        }
        this.content.add(entry);
    }

    public List<Attributable> getEntries(){
        if(this.content == null){
            this.content = new ArrayList<Attributable>();
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
                if(this.content.get(i) instanceof Keywordable){
                    total ++;
                }
            }
            return total;
        }
    }

    public List<Attributable> findEntriesByAuthor(String author){
        ArrayList<Attributable> a = new ArrayList<Attributable>();
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
                if(elt instanceof Timestampable){
                   if(((Timestampable) elt).getTimestamp() >= t){
                        t = ((Timestampable) elt).getTimestamp();
                        l = (Timestampable) elt;
                    } 
                }
                
            }
            return l;
        }
    }

    public List<Keywordable> findEntriesByKeywords(String[] keywords){
        ArrayList<Keywordable> a = new ArrayList<Keywordable>();
        if(this.content == null || this.content.size() == 0){
            return a;
        }
        else{
            for(Attributable elt : this.content){
                if(elt instanceof Keywordable){
                    Keywordable k = (Keywordable) elt;
                    boolean b = true;
                    for(String s : keywords){
                        if(!k.getKeywords().contains(s)){
                            b = false;
                        }
                    }
                    if(b){
                        a.add(k);
                    }
                }
                
            }
            return a;
        }

    }
    //au moins un des mot dans le contenu
    public List<Article> findEntriesByContent(String[] str){
        ArrayList<Article> a = new ArrayList<Article>();

            for(Attributable elt : this.content){
                if(elt instanceof Article){
                    boolean b = true;
                    Article temp = (Article) elt;
                    for(String s : str){
                        if(!temp.getContent().contains(s)){
                            b = false;
                        }
                    }
                    if(b){
                        a.add(temp);
                    }
                }
                
                
            }
            return a;

    }

    public List<AbstractEntry> findEntriesByKeywordsOrContent(String[] keywords){
        ArrayList<Article> c = (ArrayList<Article>) findEntriesByContent(keywords);
        ArrayList<Keywordable> k = (ArrayList<Keywordable>) findEntriesByKeywords(keywords);
        ArrayList<AbstractEntry> tab = new ArrayList<AbstractEntry>();
        for(Article elt :c ){
            AbstractEntry r = (AbstractEntry) elt;
            tab.add(r);
        }
        for(Keywordable elt : k ){
            AbstractEntry r = (AbstractEntry) elt;
            if(!tab.contains(r)){
                tab.add(r);
            }
        }
        return tab;
    }
}
