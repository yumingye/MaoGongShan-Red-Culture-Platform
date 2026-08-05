<template>
  <section class="photo-compare">
    <SafeImage :src="after" :alt="afterLabel" />
    <div class="before-layer" :style="{ width: `${value}%` }"><SafeImage :src="before" :alt="beforeLabel" /></div>
    <span class="label before">{{ beforeLabel }}</span><span class="label after">{{ afterLabel }}</span>
    <div class="divider" :style="{ left: `${value}%` }"><i>↔</i></div>
    <input v-model="value" type="range" min="5" max="95" aria-label="拖动查看图片对比" />
  </section>
</template>
<script setup>import{ref}from'vue';import SafeImage from'./SafeImage.vue';defineProps({before:String,after:String,beforeLabel:{type:String,default:'资料图 A'},afterLabel:{type:String,default:'资料图 B'}});const value=ref(50)</script>
<style scoped>.photo-compare{position:relative;min-height:clamp(340px,55vw,600px);overflow:hidden;background:#3a1115;border-radius:14px}.photo-compare>:deep(.safe-image){position:absolute;inset:0;width:100%;height:100%}.before-layer{position:absolute;inset:0 auto 0 0;z-index:2;overflow:hidden}.before-layer>:deep(.safe-image){width:calc(100vw - 48px);max-width:1200px}.divider{position:absolute;z-index:4;top:0;bottom:0;width:3px;background:#fff;transform:translateX(-50%);pointer-events:none}.divider i{position:absolute;top:50%;left:50%;display:grid;place-items:center;width:48px;height:48px;color:var(--red-dark);background:#fff;border-radius:50%;font-style:normal;transform:translate(-50%,-50%);box-shadow:0 5px 20px rgba(0,0,0,.3)}input{position:absolute;z-index:5;inset:0;width:100%;height:100%;opacity:0;cursor:ew-resize}.label{position:absolute;z-index:3;top:18px;padding:8px 12px;color:#fff;background:rgba(49,8,11,.75);border-radius:6px}.label.before{left:18px}.label.after{right:18px}</style>
