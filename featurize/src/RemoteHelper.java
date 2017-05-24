import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import opennlp.tools.chunker.ChunkerME;
import opennlp.tools.chunker.ChunkerModel;
import org.codehaus.jettison.json.JSONException;
import org.codehaus.jettison.json.JSONObject;

import java.io.*;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.*;

/**
 * The input data in data/restaurantReviews.json is set of all resturant reviews for Phoenix, AZ.
 *
 * This class creates n-grams and corresponding feature vector for the review text in this file.
 * These n-grams are created on the fly and sent over a UDP socket to the python process that
 * performs the actual classification.
 *
 * We use this approach since the performance of NLP libraries in python for large dataset is
 * poor compared the the Java library.
 */
public class RemoteHelper {

    private ChunkerME chunker;
    private MaxentTagger tagger;
    private static Set<String> foodDictionary = new HashSet<String>();
    private static Set<String> cookingStyles;
    private static Set<String> importantVerbsClass1;

    private static final HashSet<String> relevantAdjectivesSet = new HashSet<String>();


    private static final HashSet<String> posBlacklist;

    private static final HashSet<String> startEndBlacklist;

    static {
        String [] cooking_styles = new String[] {
                "baked", "bake",
                "fried", "fry",
                "broiled", "broil",
                "boiled", "boil",
                "braised", "braise",
                "deep fried", "deep fry",
                "deep-fried", "deep-fry",
                "grilled", "grill",
                "poached", "poach",
                "sauteed", "saute",
                "steamed", "steam",
                "stewed", "stew",
                "toasted", "toast",
                "roasted", "roast",
                "bbq",
                "stir-fried", "stir-fry",
                "stir fried", "stir fry",
                "barbecued", "barbecue",
                "simmering", "simmer",
                "simmered",
                "glazed", "glaze",
                "grated", "grate",
                "shredded", "shred",
                "sliced", "slice",
                "diced", "dice",
                "chopped", "chop",
                "marinated", "marinate",
                "stuffed", "stuff"
        };

        String [] imp_verbs_cl1 = new String [] {
                "ordered", "orders", "order", "ate", "eats", "eat", "drank",
                "drinks", "drink", "tried", "try", "tries", "tasted", "taste", "tastes", "liked", "like",
                "likes", "enjoyed", "enjoys", "enjoy", "took", "take", "takes", "gets", "get", "got",
                "loves", "love", "loved", "had", "has", "have", "served", "serve", "serves", "craved",
                "crave", "craves", "craving", "went", "go", "goes", "adored", "adore", "adores"

        };

        String [] posArray = new String[] {"NN", "NNS", "NNPS", "FW", "NNP"};

        // PREPOSITION not allowed at start and end
        String [] startEndBlack = new String [] {
            "IN",
        };

        String [] posBlack = new String[] {
                "CC", "DT", "EX",
                "JJR", "JJS",
                "MD", "PDT", "POS",
                "PRP", "PRP$", "RBR",
                "TO", "UH", "VBG", "VBZ",
                "WDT", "WP", "WP$", "WRB"};


        cookingStyles = new HashSet<String>(Arrays.asList(cooking_styles));

        importantVerbsClass1 = new HashSet<String>(Arrays.asList(imp_verbs_cl1));
        
        posBlacklist = new HashSet<String>(Arrays.asList(posBlack));
        startEndBlacklist = new HashSet<String>(Arrays.asList(startEndBlack));
    }

    public static String relevantAdjectives =
            "Acidic Acrid Aged Bitter Bittersweet Bland Burnt Buttery Chalky Cheesy Chewy Chocolaty Citrusy " +
                    "Cool Creamy Crispy Crumbly Crunchy Crusty Doughy Dry Earthy Eggy Fatty Fermented Fiery " +
                    "Fishy Fizzy Flakey Flat Flavorful Fresh Fried Fruity Full-bodied Gamey Garlicky Gelatinous " +
                    "Gingery Glazed Grainy Greasy Gooey Gritty Harsh Hearty Heavy Herbal Hot Icy Infused Juicy " +
                    "Lean Light Lemony Malty Mashed Meaty Mellow Mild Minty Moist Mushy Nutty Oily Oniony Overripe " +
                    "Pasty Peppery Pickled Plain Powdery Raw Refreshing Rich Ripe Roasted Robust Rubbery Runny Salty " +
                    "Sauteed Savory Seared Seasoned Sharp Silky Slimy Smokey Smothered Smooth Soggy Soupy Sour Spicy " +
                    "Spongy Stale Sticky Stale Stringy Strong Sugary or sweet Sweet-and-sour Syrupy Tangy Tart " +
                    "Tasteless Tender Toasted Tough Unflavored Unseasoned Velvety Vinegary Watery Whipped Woody " +
                    "Yeasty Zesty Zingy";


    void LOG(String s) {
        //System.out.println(s);
    }

    public void loadFoodDictionary() {
        // Create the file
        File file = new File("data/foodName.txt");
        if (!file.exists()) {
            LOG("Could not find foodName.txt file");
            return;
        }

        FileReader fr = null;
        try {
            fr = new FileReader(file.getAbsoluteFile());
        } catch (IOException e) {
            LOG("Unable to open file foodName.txt for writing. Please retry. Exception: " + e.getMessage());
        }

        BufferedReader br = new BufferedReader(fr);

        String line = "";
        try {
            while((line = br.readLine()) != null) {
                line = line.trim().toLowerCase();
                if(line.isEmpty())
                    continue;;

                line = line.toLowerCase();
                foodDictionary.add(line);
            }

            foodDictionary.remove("of");
            foodDictionary.remove("hot");
            foodDictionary.remove("four");
            foodDictionary.remove("in");
            foodDictionary.remove("love");
            foodDictionary.remove("club");

        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            if(br != null)
                br.close();
        } catch (IOException e) {
            // Ignore these exceptions
        }

        try {
            if(fr!=null)
                fr.close();
        } catch (IOException e) {
            // Ignore
        }
    }

    public static class StructureArray {
        final String [] posArray;
        final String [] strArray;
        final String [] npArray;

        public StructureArray(String[] posArray, String[] strArray, String[] npArray) {
            this.posArray = posArray;
            this.strArray = strArray;
            this.npArray = npArray;
        }
    };

    public static StructureArray phraseClassifier1(String str, MaxentTagger tagger, ChunkerME chunker) {
        String taggedStr = tagger.tagString(str);
        String [] tagToks = taggedStr.split(" ");

        String[] tags = new String[tagToks.length];
        String [] strToks = new String[tagToks.length];
        for (int i = 0; i < tagToks.length; i++) {
            int k = tagToks[i].lastIndexOf("_");

            tags[i] = tagToks[i].substring(k+1);
            strToks[i] = tagToks[i].substring(0, k);
        }

        String [] phraseToks = chunker.chunk(strToks, tags);


        return new StructureArray(tags, strToks, phraseToks);
    }

    public void extractFeaturesForFile(String ipFile, String opFileDishNames, String opFileFeatures, boolean includeHeader, boolean isSend) {

        // Create the file
        //All samples
        File file = new File(ipFile);

        if (!file.exists()) {
            LOG("Could not find file");
            return;
        }

        FileReader fr = null;
        try {
            fr = new FileReader(file.getAbsoluteFile());
        } catch (IOException e) {
            LOG("Unable to open file for writing. Please retry. Exception: " + e.getMessage());
        }

        BufferedReader br = new BufferedReader(fr);

        InputStream modelIn = null;
        FileWriter featureFW = null;
        BufferedWriter featureBW = null;
        FileWriter labelFW = null;
        BufferedWriter labelBW = null;

        try {

            ReturnData returnData = new ReturnData();
            negativeFeatures(br, tagger, chunker, returnData, isSend);

            // Write it out

            // Create the file to saving training data
            File lbFile = new File(opFileDishNames);
            if (!lbFile.exists()) {
                try {
                    lbFile.createNewFile();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            } else {
                lbFile.delete();
            }

            File featureFile = new File(opFileFeatures);
            if (!featureFile.exists()) {
                try {
                    featureFile.createNewFile();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            } else {
                featureFile.delete();
            }

            try {
                featureFW = new FileWriter(featureFile.getAbsoluteFile());
            } catch (IOException e) {
                LOG("Unable to open file for writing. Please retry. Exception: " + e.getMessage());
            }

            try {
                labelFW = new FileWriter(lbFile.getAbsoluteFile());
            } catch (IOException e) {
                LOG("Unable to open file for writing. Please retry. Exception: " + e.getMessage());
            }

            featureBW = new BufferedWriter(featureFW);
            labelBW = new BufferedWriter(labelFW);

            if(includeHeader == true) {
                featureBW.write(header() + "\n");
            }

            if(!isSend) {
                for (int i = 0; i < returnData.featureVector.size(); i++) {
                    String featureVect = "";
                    int[] currFeatureVec = returnData.featureVector.get(i);

                    for (int j = 0; j < currFeatureVec.length; j++) {
                        featureVect += currFeatureVec[j] + ",";
                    }
                    featureVect = featureVect.substring(0, featureVect.length() - 1);
                    featureBW.write(featureVect + "\n");
                }
            }

        }
        catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (modelIn != null) {
                try {
                    modelIn.close();
                } catch (IOException e) {
                }
            }
            try {
                if (featureBW != null)
                    featureBW.close();
            } catch (IOException e) {
                // Ignore these exceptions
            }

            try {
                if (featureFW != null)
                    featureFW.close();
            } catch (IOException e) {
                // Ignore
            }

            try {
                if (labelBW != null)
                    labelBW.close();
            } catch (IOException e) {
                // Ignore these exceptions
            }

            try {
                if (labelFW != null)
                    labelFW.close();
            } catch (IOException e) {
                // Ignore
            }

            try {
                if (br != null)
                    br.close();
            } catch (IOException e) {
                // Ignore these exceptions
            }

            try {
                if (fr != null)
                    fr.close();
            } catch (IOException e) {
                // Ignore
            }
        }
    }

    private void negativeFeatures(BufferedReader br, MaxentTagger tagger, ChunkerME chunker, ReturnData returnData, boolean isSend)
            throws IOException, JSONException {
        DatagramSocket socket=null;
        InetAddress address = null;
        if(isSend) {
            socket = new DatagramSocket();
            address =  InetAddress.getByName("localhost");
        }
        String line = "";

        System.out.println("Sending n-grams details to python process: ");

        while((line = br.readLine()) != null) {
            JSONObject job = new JSONObject(line);
            String uidBidrId = job.getString("user_id") + "," + job.get("business_id") + "," +
                                job.get("review_id") + "," + job.get("stars");
            processReviewText(job.getString("text"), returnData, uidBidrId, socket, address);
        }

        if(isSend) {
            DatagramPacket packet = new DatagramPacket("done".getBytes(), "done".getBytes().length, address, 10000);
            socket.send(packet);
        }
    }

    public void processReviewText(String text,
                                  ReturnData returnData, String uidBidrId, DatagramSocket socket, InetAddress address) throws IOException {
        //Split the text by .
        String [] reviewSentence = text.split("\\.");

        for (int i = 0; i < reviewSentence.length; i++) {
            String str = reviewSentence[i].trim();

            // Perform cleanup
            if (str.length() == 0)
                continue;

            str.replace("\\n", "");

            String[] sa = str.split(" ");
            boolean sentenceContainsFood = false;
            boolean sentenceContainsStyle = false;
            boolean sentenceContainsImpVerb = false;
            boolean sentenceContainsImpAdj = false;
            for (int j = 0; j < sa.length; j++) {
                if (foodDictionary.contains(sa[j].toLowerCase())) {
                    sentenceContainsFood = true;
                }
                if (cookingStyles.contains(sa[j].toLowerCase())) {
                    sentenceContainsStyle = true;
                }
                if (importantVerbsClass1.contains(sa[j].toLowerCase())) {
                    sentenceContainsStyle = true;
                }
                if (relevantAdjectivesSet.contains(sa[j].toLowerCase())) {
                    sentenceContainsImpAdj = true;
                }
            }

            StructureArray sentenceSegments = phraseClassifier1(str, tagger, chunker);

            //Split the array into sequences of max size 6
            int MAX_SZ = 6;
            List<String[]> itemNames = new ArrayList<String[]>();
            List<String[]> itemPos = new ArrayList<String[]>();
            List<String[]> itemPhrase = new ArrayList<String[]>();
            String[] theStr = sentenceSegments.strArray;
            String[] thePOS = sentenceSegments.posArray;
            String[] thePhrase = sentenceSegments.npArray;

            int strLen = sentenceSegments.strArray.length;
            int subStrLen = strLen >= MAX_SZ ? MAX_SZ : strLen;
            for (int start = 0; start < strLen; start++) {
                for (int end = start + 2;/* end <= (start + subStrLen) && */end <= strLen; end++) {
                    itemNames.add(Arrays.copyOfRange(theStr, start, end));
                    itemPos.add(Arrays.copyOfRange(thePOS, start, end));
                    itemPhrase.add(Arrays.copyOfRange(thePhrase, start, end));
                }
            }

            extractFeaturesAndLabels(itemPos, itemNames, itemPhrase, sentenceContainsFood,
                    sentenceContainsStyle, sentenceContainsImpVerb, sentenceContainsImpAdj, returnData, uidBidrId, socket, address);
        }
    }

    static public class ReturnData {
        public  List<int[]>  featureVector = new ArrayList<int[]>();
        public  List<String>  dishNames = new ArrayList<String>();
        public List<String> details = new ArrayList<String>();
    }


    public enum Features{
        BEGINS_RELV_VB_AJ_NOUN,

        ENDS_NF,

        FOOD_UNIT_OR_SENTENCE_CLUE,

        ALL_IN_NP_WITH_CLUE,


        IS_DISH
    };


    public void extractFeaturesAndLabels(List<String[]> itemPos, List<String[]> itemNames, List<String[]> itemPhrase,
                                         boolean sentenceContainsFood, boolean sentenceContainsStyle,
                                         boolean sentenceContainsImpVerb, boolean sentenceContainsImpAdj,
                                         ReturnData returnData, String uidBidrId, DatagramSocket socket, InetAddress address)
            throws IOException {


        // For each item name
        for (int k = 0; k < itemPos.size(); k++) {
            //Clean up unexpected tokens

            int foodName = 0, cookingStyle = 0, relevantAdjective = 0, areAllWordsInSameNP = 1;
            int numConsecutiveNNP = 0, maxNumConsecutiveNNP = 0;

            int maxNumConsecutiveNouns = 0, numConsecutiveNouns = 0;

            int[] features = new int[Features.values().length];
            boolean skipThis = false;

            //For each word in the item
            for (int j = 0; j < itemPos.get(k).length; j++) {
                String strToken = itemNames.get(k)[j].trim().toLowerCase();
                String posToken = itemPos.get(k)[j].trim();
                String phraseToken = itemPhrase.get(k)[j].trim();

                if(posBlacklist.contains(posToken)) {
                    skipThis = true;
                    break;
                }

                int start = 0, end = itemPos.get(k).length-1;
                if(startEndBlacklist.contains(itemPos.get(k)[start]) ||
                        startEndBlacklist.contains(itemPos.get(k)[end])) {
                    skipThis = true;
                    break;
                }

                // # Relevant adjectives
                if (j!= itemPos.get(k).length-1 && relevantAdjectivesSet.contains(strToken))
                    relevantAdjective = 1;

                // # Food name
                if (foodDictionary.contains(strToken))
                    foodName = 3;

                // # cooking style
                if (cookingStyles.contains(strToken))
                    cookingStyle = 1;

                // Are all words in same NP
                if (!phraseToken.endsWith("-NP")) {
                    areAllWordsInSameNP = 0;
                }

                // # Noun family
                // # Consecutive Nouns
                if (posToken.contains("NN") ||
                        posToken.contains("NNS") ||
                        posToken.contains("NNPS") ||
                        posToken.contains("FW") ||
                        posToken.contains("NNP") ||
                        posToken.contains("FW")) {
                    numConsecutiveNouns++;
                } else {
                    if (maxNumConsecutiveNouns < numConsecutiveNouns) {
                        maxNumConsecutiveNouns = numConsecutiveNouns;
                        numConsecutiveNouns = 0;
                    }
                }

                // # consecutive NNP
                if (posToken.contains("NNP")) {
                    numConsecutiveNNP++;
                } else {
                    if (maxNumConsecutiveNNP < numConsecutiveNNP) {
                        maxNumConsecutiveNNP = numConsecutiveNNP;
                        numConsecutiveNNP = 0;
                    }
                }
            }

            if(skipThis) {
                continue;
            }

            String[] posArr = itemPos.get(k);
            int end = posArr.length - 1;

            features[Features.BEGINS_RELV_VB_AJ_NOUN.ordinal()] =
                    (relevantAdjective != 0 || isNounFamily(posArr, 0) || cookingStyle != 0) ? 1 : 0;

            features[Features.ENDS_NF.ordinal()] = isNounFamily(posArr, end) ? 1 : 0;

            boolean clue = (sentenceContainsFood || sentenceContainsImpAdj || sentenceContainsImpVerb
                            || sentenceContainsStyle);

            features[Features.FOOD_UNIT_OR_SENTENCE_CLUE.ordinal()] = clue || foodName>0 ? 1 : 0;

            features[Features.ALL_IN_NP_WITH_CLUE.ordinal()] = areAllWordsInSameNP > 0 && sentenceContainsFood ? 1 : 0;

              //Is Dish always set to 1 but needs to changed in final csv
            features[Features.IS_DISH.ordinal()] = 1;

            returnData.featureVector.add(features);

            returnData.details.add(uidBidrId);
            String out = "";
            for (int t = 0; t < itemNames.get(k).length; t++) {
                out += itemNames.get(k)[t] + " ";
            }
            returnData.dishNames.add(out);

            String featureVect = "";
            for (int j = 0; j < features.length; j++) {
                featureVect += features[j] + ",";
            }
            featureVect = featureVect.substring(0, featureVect.length() - 1);


            if(socket != null && address != null) {
                String tuple = out.trim() + "\t" + featureVect + "\t" + uidBidrId;
                byte[] buf = tuple.getBytes();
                DatagramPacket packet = new DatagramPacket(buf, buf.length, address, 10000);
                socket.send(packet);
                try {
                    Thread.sleep(25);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    private boolean isNounFamily(String[] posArr, int where) {
        return posArr[where].contains("NN") ||
                posArr[where].contains("NNS") ||
                posArr[where].contains("NNP") ||
                posArr[where].contains("NNPS") ||
                posArr[where].contains("FW");
    }

    public RemoteHelper() {
        InputStream modelIn = null;
        try {
            tagger = new MaxentTagger("stanford-postagger-2014-08-27/models/english-left3words-distsim.tagger");

            modelIn = new FileInputStream("opennlp/en-chunker.bin");
            ChunkerModel chunkerModel = new ChunkerModel(modelIn);
            chunker = new ChunkerME(chunkerModel);

            //Then load food dictionary
            loadFoodDictionary();

            loadRelevantAdjectives();

        } catch(Exception e) {
            e.printStackTrace();
        }
    }

    private void loadRelevantAdjectives() {
        String [] strs = relevantAdjectives.split(" ");
        for (String s : strs) {
            relevantAdjectivesSet.add(s.toLowerCase());
        }
    }

    private String header() {
        String header = "";
        for(Features h : Features.values()) {
            header += h.name() + ",";
        }

        return header.substring(0, header.length()-1);
    }


    public static void main(String[] args) {
        RemoteHelper m = new RemoteHelper();

        m.extractFeaturesForFile("data/restaurantReviews.json",
                "output/testDishname.txt",
                "output/testFeatures.csv", true, true);


    }

    public static class SentenceSegments {
        public final String [] phrasesWithPOS;
        public final String [] phrases;

        SentenceSegments(String[] phrasesWithPOS, String[] phrases) {
            this.phrasesWithPOS = phrasesWithPOS;
            this.phrases = phrases;
        }
    }

    public static SentenceSegments phraseClassifier(String str, MaxentTagger tagger, ChunkerME chunker) {
        String taggedStr = tagger.tagString(str);
        String [] tagToks = taggedStr.split(" ");

        String[] tags = new String[tagToks.length];
        String [] strToks = new String[tagToks.length];
        for (int i = 0; i < tagToks.length; i++) {
            int k = tagToks[i].lastIndexOf("_");

            tags[i] = tagToks[i].substring(k+1);
            strToks[i] = tagToks[i].substring(0, k);
        }

        String [] phraseToks = chunker.chunk(strToks, tags);

        String lastPhrase = "";
        String segment = "";
        List<String> phraseChunks = new ArrayList<String>();
        String segmentPos = "";
        List<String> phraseChunksPos = new ArrayList<String>();
        for (int i = 0; i < phraseToks.length; i++) {
            int k = phraseToks[i].lastIndexOf("-");
            String currPhrase;
            if(k<0) {
                currPhrase = phraseToks[i];
            } else {
                currPhrase = phraseToks[i].substring(k+1);
            }

            if(!lastPhrase.isEmpty() && !lastPhrase.equals(currPhrase)) { // Add the segment
                segment = "[" + lastPhrase + "\\" + segment.trim() + "]";
                segmentPos = "[" + lastPhrase + "\\" + segmentPos.trim() + "]";
                phraseChunks.add(segment);
                phraseChunksPos.add(segmentPos);
                segment = "";
                segmentPos = "";
            }

            segment += " " + strToks[i];
            segmentPos += " " + tagToks[i];
            lastPhrase = currPhrase;
        }

        if(!lastPhrase.isEmpty()) { // Add the segment
            segment = "[" + lastPhrase + "\\" + segment.trim() + "]";
            segmentPos = "[" + lastPhrase + "\\" + segmentPos.trim() + "]";
            phraseChunks.add(segment);
            phraseChunksPos.add(segmentPos);
        }

        String [] phraseChunkArray = new String[phraseChunks.size()];
        String [] phraseChunkPosArray = new String[phraseChunks.size()];
        for (int i = 0; i < phraseChunks.size(); i++) {
            phraseChunkArray[i] = phraseChunks.get(i);
            phraseChunkPosArray[i] = phraseChunksPos.get(i);
        }

        return new SentenceSegments(phraseChunkPosArray, phraseChunkArray);
    }
}