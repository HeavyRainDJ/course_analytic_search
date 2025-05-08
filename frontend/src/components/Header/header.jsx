import React from "react";
import styles from './header.module.css';
import { Link } from "react-router-dom";

function Header() {
    return (
        <div className={styles.header}>
            <div className={styles.labels_text}>
                <p className={styles.crypto_text}>AnalyticSearch</p>
                <div className={styles.right_text}>
                    <Link to="/Main" className={styles.links_text}>
                        Главная страница
                    </Link>
                    <Link to="/Search" className={styles.links_text}>
                        Поиск
                    </Link>
                </div>
            </div>
            <div className={styles.palka}></div> 
        </div>
    );
}

export default Header;
