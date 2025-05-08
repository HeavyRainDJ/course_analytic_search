import React from "react";
import styles from './mainPage.module.css'
import Header from "../../components/Header/header.jsx";
import Circle from "../../components/Component_circle/circle_round.jsx";

function Main() {
  return (
    <div className={styles.main}>
      <div className={styles.main_head}>
        <Header/>
      </div>
      <div className={styles.main_circle}>
        <Circle/>
      </div>

    </div>
  );
}

export default Main;
