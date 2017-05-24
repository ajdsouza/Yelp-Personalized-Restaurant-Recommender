<?php 
    $user_id = $_POST['user_id'];
    //$user_id = "6CfB1MEvy7AQkP0Mpbsrjw";
    if (isset($user_id)) {
        $db = new SQLite3('Data/datatouille.db');
        $restaurants = [];
        $dishes = [];
        $results = $db->query("SELECT * FROM recommendations WHERE user_id LIKE '".$user_id."'");
        while ($row = $results->fetchArray()) {
          for ($x = 1; $x <= 6; $x++) {
              $dishes[] = $row["d".$x];
          } 
        }
          
        for ($x = 0; $x < 6; $x++) {
          $results = $db->query("SELECT restaurant_id FROM specialties JOIN yelp_restaurants ON restaurant_id == business_id WHERE dish_ids LIKE '%".$dishes[$x]."%' AND restaurant_id NOT IN ('".implode("','",$restaurants)."') LIMIT 1");
          $counter = $x + 1;
          while ($restaurant = $results->fetchArray()) {
            $restaurants[] = $restaurant['restaurant_id'];
            $results0 = $db->query("SELECT * FROM yelp_restaurants WHERE business_id LIKE '".$restaurant['restaurant_id']."'");
            while ($row = $results0->fetchArray()) {
              echo "<div id=\"r".$counter."\">";
              echo "<div class=\"marker\" id=\"latitude\">".$row["latitude"]."</div>";
              echo "<div class=\"marker\" id=\"longitude\">".$row["longitude"]."</div>";
              echo "<div class=\"restaurantName\">".$row["name"]."</div>";
              $results1 = $db->query("SELECT * FROM specialties WHERE restaurant_id LIKE '".$row["business_id"]."'");
              while ($row1 = $results1->fetchArray()) {
                $comp = preg_split('/\s+/', $row1["dish_ids"]);
                $dishQuery = "SELECT * FROM dishes WHERE dish_id IN ('".implode("','",$comp)."')";
                $dish = [];
                $dishResults = $db->query($dishQuery);
                while ($r = $dishResults->fetchArray()) {
                  $dish[] = $r["dish_name"];
                }
              }
              echo "<div class=\"specialties\">Specialties: ".implode(", ",$dish)."</div>";
              echo "<div class=\"address\">".str_replace("Phoenix","<br />Phoenix",$row["full_address"])."</div>";
              echo "<div class=\"starRating\">Rating: ".$row["stars"]."</div>";
              echo "<div class=\"numReviews\">Number of Reviews: ".$row["review_count"]."</div>";
              echo "</div><hr />";
            }
          }
        }
    } else {
      echo "Incorrect Inputs";
    }
?>
