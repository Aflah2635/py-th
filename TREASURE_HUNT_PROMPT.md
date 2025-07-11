 Create an Advanced Treasure Hunt Web Application

---

### 🧩 Project Title:

**"Digital Treasure Hunt – Cyberpunk Edition"**

---

### ⚙️ Core Stack:

* **Backend:** Python Django
* **Frontend:** HTML, CSS, Tailwind (optional)
* **Database:** SQLite 
* **Deployment:** Compatible with PythonAnywhere

---

### 🧠 Features to Implement:

#### 1. 🔐 **User System**

* User Registration & Login
* Show/hide password toggle on input fields
* Track user activity (login, logout, register)

#### 2. 🎯 **Treasure Hunt Game Core**

* Clues shown one-by-one in order
* Each clue includes:

  * Question text
  * Optional image or puzzle
  * Input field for answer
  * Button to request a hint
* Hints are stored in DB and linked to specific clues
* Record:

  * Correct answer
  * Wrong answers
  * Time taken per clue
  * Whether hint was used

---

#### 3. 🏆 **Leaderboard System**

* Display list of players sorted by:

  * **Primary:** Score (descending)
  * **Secondary:** Completion time (ascending)
* Show top 10 players on home/dashboard
* Highlight top 3 (Gold, Silver, Bronze styling)
* Recalculate ranks live or on refresh

---

#### 4. 📊 **Admin Panel Features**

* Full access to:

  * Create/edit/delete clues and hints
  * Activate/deactivate questions individually or in bulk
* New section: `Logs`

  * Subsections for:

    * Login/logout/register
    * Clue solved
    * Wrong attempts
    * Hints used
    * Completion events
* Ability to activate/deactivate **all** questions with a single click

---

#### 5. 🧾 **Game State Control**

* If **no active questions**, display:

  * `"😕 Questions are currently not available. Please check back later."`
* Prevent game from completing when no clues are available

---

#### 6. 🔔 **Discord Bot Integration**

* Use **Discord Webhooks** to send activity logs to separate channels:

  * Clue Solved
  * Hint Used
  * User Activity (login, logout, registration)
* Format all messages as **Embeds**

  * Use different colors per section (e.g., green for solve, red for wrong)


---

#### 7. 📈 **Analytics Dashboard (Admin Only)**

* Visual insights:

  * Solved % per clue
  * Average time per clue
  * Hint usage rate
  * Player drop-off point
  * Fastest solver per clue
* Charts:

  * Bar graph: Solved vs Clue
  * Line chart: Solve time
  * Pie chart: Hint usage
  * Heatmap: Player activity by time
* Dashboard locked to staff/superusers

---

#### 8. 💡 **Additional UX Features**

* Clean UI with themes like:

  * Cyberpunk

* Navigation bar with:

  * Dashboard
  * Hunt Progress
  * Leaderboard
* Store player’s progress (score, time, used hints, wrong attempts)
* When hunt is completed, show a congratulations screen with final score and time

---

### 🚫 Disabled Features (Do Not Include):

* LLM assistant for solving clues
* Glitch effect animations
* Achievements/Badges

