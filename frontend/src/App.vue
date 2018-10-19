<template>
  <div class="flex justify-center" id="app">

    <div id="form" class="p-8 flex flex-col bg-grey-lighter rounded mt-8">

      <div class="w-full mb-4">

      <label class="block mb-2" for="name">Title</label>
      <input class="border-2 border-grey-light rounded-sm p-2 w-full" type="text" id="name" name="name">

      

     </div>

    <div class="w-full mb-4">

      <label class="block mb-2" for="description">Description</label>
      <textarea class="border-2 border-grey-light rounded-sm p-2 w-full"  v-model="desc" name="description" id="description"  rows="4"></textarea>
    
     <div class="mt-2">
          <p v-text="info"></p>
      </div>

    </div>

    <button class="bg-blue-light text-white uppercase text-xs p-2 rounded-sm" @click="analyse">Validate</button>

    </div>

  </div>

</template>

<script>
import HelloWorld from "./components/HelloWorld.vue";
import axios from 'axios';

  // Petite maison de vacances, dans un quartier calme. ok
  // Petite maison de vacances, dans un quartier calme mais sale. p
  // Charmante petite maison de vacances pleine de vie, dans un quartier calme mais sale. neg
  // Immeuble, nécessite quelques rénovations.

export default {
  name: "app",
  components: {
    HelloWorld
  },

  data() { return {
    desc: "", 
    info: ""
  }},

  methods: {

    analyse() {

      let text = this.desc

      axios.post('http://127.0.0.1:5000/compare', {
          description: text,
        })
        .then( (response) => {

            console.log(response.data)

            if (response.data.positive[0]  >= response.data.positive[1] + 0.09) {
              this.info = "It might be too positive, calm it down a notch."
            }

            else if (response.data.negative[0] >= response.data.negative[1] + 0.04) {
              this.info = "You sound a bit negative, aren't you ? Cheer up !"
            }

            else if (response.data.neutral[0] >= response.data.neutral[1] + 0.09) {
              this.info = "It feels a bit to neutral, put some more live in it !"
            }

            else {
              this.info = ""
            }

        })
        .catch(function (error) {
          console.log(error);
        });

    }

  }
};
</script>

<style>
#form {
  width: 600px;
}
</style>
