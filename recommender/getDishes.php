<?php 
    $user_id = $_POST['user_id'];
    //$user_id = "6CfB1MEvy7AQkP0Mpbsrjw";
    if (isset($user_id)) {
        $db = new SQLite3('Data/datatouille.db');
        $results1 = $db->query("SELECT * FROM user_dish_preferences WHERE user_id LIKE '".$user_id."'");
        while ($row = $results1->fetchArray()) {
          $comp = preg_split('/\s+/', $row["dishes"]);
          $dishQuery = "SELECT * FROM dishes WHERE dish_id IN ('".implode("','",$comp)."')";
          $dishes = [];
          $dishResults = $db->query($dishQuery);
          while ($r = $dishResults->fetchArray()) {
            $dishes[] = $r["dish_name"];
          }
          echo "<div id=\"userDishPreferences\">User Preferred Dishes: ".implode(", ",$dishes)."</div>\n";
        }
        
        $results2 = $db->query("SELECT * FROM recommendations WHERE user_id LIKE '".$user_id."'");
        while ($row = $results2->fetchArray()) {
          $comp = [];
          for ($x = 1; $x <= 6; $x++) {
              $comp[] = $row["d".$x];
          } 
          $dishQuery = "SELECT * FROM dishes WHERE dish_id IN ('".implode("','",$comp)."')";
          $dishes = [];
          $dishResults = $db->query($dishQuery);
          while ($r = $dishResults->fetchArray()) {
            $dishes[] = $r["dish_name"];
          }
          echo "<div id=\"userDishRecommendations\">Recommended Dishes: <div id=\"d1\" value=\"".$row["d1"]."\">".$dishes[0]."</div>, <div id=\"d2\" value=\"".$row["d2"]."\">".$dishes[1]."</div>, <div id=\"d3\" value=\"".$row["d3"]."\">".$dishes[2]."</div>, <div id=\"d4\" value=\"".$row["d4"]."\">".$dishes[3]."</div>, <div id=\"d5\" value=\"".$row["d5"]."\">".$dishes[4]."</div>, <div id=\"d6\" value=\"".$row["d6"]."\">".$dishes[5]."</div></div>\n";
        }
    } else {
      echo "Incorrect Inputs";
    }

?>
