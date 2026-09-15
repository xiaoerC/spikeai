<template>
  <div class="app-container">
    <div class="app-container-inner">
      <div class="wscn-http403-container">
        <div class="wscn-http403">
          <div class="pic-403">
            <img class="pic-403__parent" src="@/assets/403_images/403.png" alt="403" />
            <img class="pic-403__child left" src="@/assets/403_images/403_cloud.png" alt="403" />
            <img class="pic-403__child mid" src="@/assets/403_images/403_cloud.png" alt="403" />
            <img class="pic-403__child right" src="@/assets/403_images/403_cloud.png" alt="403" />
          </div>
          <div class="bullshit">
            <div class="bullshit__oops">您没有访问权限！</div>
            <div class="bullshit__info">请检查URL地址是否正确, 或点击回到首页。</div>
            <router-link to="/" class="bullshit__return-home">回到首页</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup></script>

<style lang="scss" scoped>
  .wscn-http403-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  a {
    text-decoration: none;
  }

  .wscn-http403 {
    display: flex;
    position: relative;
    align-items: center;
    justify-content: center;
    width: 1200px;
    padding: 0 50px;
    overflow: hidden;

    .pic-403 {
      position: relative;
      width: 600px;
      float: left;
      overflow: hidden;

      &__parent {
        width: 100%;
      }

      &__child {
        position: absolute;

        &.left {
          top: 17px;
          left: 220px;
          width: 80px;
          animation-name: cloudLeft;
          animation-duration: 2s;
          animation-timing-function: linear;
          animation-delay: 1s;
          opacity: 0;
          animation-fill-mode: forwards;
        }

        &.mid {
          top: 10px;
          left: 420px;
          width: 46px;
          animation-name: cloudMid;
          animation-duration: 2s;
          animation-timing-function: linear;
          animation-delay: 1.2s;
          opacity: 0;
          animation-fill-mode: forwards;
        }

        &.right {
          top: 100px;
          left: 500px;
          width: 62px;
          animation-name: cloudRight;
          animation-duration: 2s;
          animation-timing-function: linear;
          animation-delay: 1s;
          opacity: 0;
          animation-fill-mode: forwards;
        }
      }
    }

    .bullshit {
      padding: 30px 0;
      float: left;
      overflow: hidden;

      &__oops {
        margin-bottom: 20px;
        animation-name: slideUp;
        animation-duration: 0.5s;
        opacity: 0;
        color: #1482f0;
        font-size: 32px;
        font-weight: bold;
        line-height: 40px;
        animation-fill-mode: forwards;
      }

      &__headline {
        margin-bottom: 10px;
        animation-name: slideUp;
        animation-duration: 0.5s;
        animation-delay: 0.1s;
        opacity: 0;
        color: #222;
        font-size: 20px;
        font-weight: bold;
        line-height: 24px;
        animation-fill-mode: forwards;
      }

      &__info {
        margin-bottom: 30px;
        animation-name: slideUp;
        animation-duration: 0.5s;
        animation-delay: 0.2s;
        opacity: 0;
        color: grey;
        font-size: 13px;
        line-height: 21px;
        animation-fill-mode: forwards;
      }

      &__return-home {
        display: block;
        width: 110px;
        height: 36px;
        float: left;
        animation-name: slideUp;
        animation-duration: 0.5s;
        animation-delay: 0.3s;
        border-radius: 100px;
        opacity: 0;
        background: #1482f0;
        color: #fff;
        font-size: 14px;
        line-height: 36px;
        text-align: center;
        cursor: pointer;
        animation-fill-mode: forwards;
      }
    }
  }

  @keyframes cloudLeft {
    0% {
      top: 17px;
      left: 220px;
      opacity: 0;
    }

    20% {
      top: 33px;
      left: 188px;
      opacity: 1;
    }

    80% {
      top: 81px;
      left: 92px;
      opacity: 1;
    }

    100% {
      top: 97px;
      left: 60px;
      opacity: 0;
    }
  }

  @keyframes cloudMid {
    0% {
      top: 10px;
      left: 420px;
      opacity: 0;
    }

    20% {
      top: 40px;
      left: 360px;
      opacity: 1;
    }

    70% {
      top: 130px;
      left: 180px;
      opacity: 1;
    }

    100% {
      top: 160px;
      left: 120px;
      opacity: 0;
    }
  }

  @keyframes cloudRight {
    0% {
      top: 100px;
      left: 500px;
      opacity: 0;
    }

    20% {
      top: 120px;
      left: 460px;
      opacity: 1;
    }

    80% {
      top: 180px;
      left: 340px;
      opacity: 1;
    }

    100% {
      top: 200px;
      left: 300px;
      opacity: 0;
    }
  }

  @keyframes slideUp {
    0% {
      transform: translateY(60px);
      opacity: 0;
    }

    100% {
      transform: translateY(0);
      opacity: 1;
    }
  }
</style>
