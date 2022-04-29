// import { Component, OnInit } from '@angular/core';

// @Component({
//   selector: 'app-show-stats',
//   templateUrl: './show-stats.component.html',
//   styleUrls: ['./show-stats.component.css']
// })
// export class ShowStatsComponent implements OnInit {

//   constructor() { }

//   ngOnInit(): void {
//   }

// }

// import { Component, OnInit } from '@angular/core';
// import 'chartjs-plugin-streaming';

// @Component({
//   selector: 'app-show-stats',
//   templateUrl: './show-stats.component.html',
//   styleUrls: ['./show-stats.component.css']
// })
// export class ShowStatsComponent implements OnInit {

//   myDataFromServer:number=20;
//   updateMyDataFromServerFunction:any;

//   datasets: any[] = [{
//     data: []
//   }, {
//     data: []
//   }];

//   options: any;
//   constructor( ) {}

//   ngOnInit(){

//     this.options= {
//       scales: {
//         xAxes: [{
//           type: 'realtime',
//           realtime: {
//             onRefresh: (chart: any) =>{
//               chart.data.datasets.forEach((dataset: any) => {  
//                 dataset.data.push({
//                   x: Date.now(),
//                   y: this.myDataFromServer
//                 });
//               });
//             },
//             delay: 2000
//           }
//         }],
//         yAxes: [{
//           ticks: {
//             max:100,
//             min:0
//           }
//         }]
//       }
//     };
//     this.updateMyDataFromServer();
//   }

//   updateMyDataFromServer(){
//     console.log('updateMyDataFromServer() called');    
//     this.updateMyDataFromServerFunction = setInterval(() => {
//       console.log('called');
//       this.myDataFromServer = Math.random() * 100;
//       console.log(this.myDataFromServer,'this.myDataFromServer');
//     },1000)
//   }
// }

import { Component, OnInit, QueryList } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import Chart from 'chart.js/auto';
import { ViewChild, ViewChildren } from '@angular/core';
import { interval, Subscription, timer } from 'rxjs';

// Chart.register(BarElement, BarController, CategoryScale, Decimation, Filler, Legend, Title, Tooltip);

@Component({
  selector: 'app-show-stats',
  templateUrl: './show-stats.component.html',
  styleUrls: ['./show-stats.component.css']
})
export class ShowStatsComponent implements OnInit {

  clicked_match_id!: number;
  details!: any;
  name!: string;
  disp_match_details: Boolean = true;
  disp_match_sum: Boolean = false;
  disp_score_comparison: Boolean = false;
  Linechart!: Chart;
  team1: number[] = [];
  team2: number[] = [];
  //match_info: venue_det[] = [];
  disp_comp = "display: None;";
  disp_pie = "display: None;";
  intervalId : any;
  runs1: number[] = [];
  counter: number = 5;
  // subscription: Subscription;

  constructor(private route: ActivatedRoute, private router: Router) { 
    this.counter=5;
    interval(1000).subscribe(x => {
      this.updatee();
  });

   }

  ngOnInit(): void {
    this.counter = 5;
    this.display_comparison_chart()
  } 

  display_comparison_chart(){

    this.disp_comp = "display: true;";
    this.disp_match_details = false;
    this.disp_match_sum = false;

    // get data for chart
    let runs2: number[] = [];
    let X_data: number[] = [];
    let count: number = 1;
    let radii1: number[] = [];
    let radii2: number[] = [];

    for(let i = 0; i < 10; i++){
      this.runs1.push(Number(this.counter + i));
      X_data.push(count);

      if(Number(count + i) > 5){
        radii1.push(3);
      }
      else{
        radii1.push(0);
      }

      radii1.push()
      count = count + 1;
    }

    for(let j = 0; j < 10; j++){
      runs2.push(Number(count + j));
  
      if(Number(count + j) > 5){
        radii2.push(3);
      }
      else{
        radii2.push(0);
      }

    }

    //get data for chart ends

    //chart

    //if(this.Linechart) this.Linechart.destroy()


    this.Linechart = new Chart('linechart',{
      type:'line',
      data:{
        labels: X_data,
        datasets:[{
          label: "test-x",
          data:this.runs1,
          borderColor:"red",
          borderWidth:1,
          tension: 0,
          pointRadius:radii1,
        },
        {
          label: "test-y",
          data:runs2,
          borderColor:"green",
          borderWidth:1,
          tension: 0,
          pointRadius: radii2
        }],
      },
      
      options:{
        responsive: false,
        scales: {
          y: {
              beginAtZero: true,
              title: {
                text: "RUNS",
                display: true
              }
          },
          x: {
            title: {
              text: "OVERS",
              display: true
            }
        },
          
      },
      elements: {
        point:{
            radius: 0
        }
    }        
      }          
    })
    //chart ends
  }

  updatee(){
    this.counter += 2;
    //this.runs1.push(this.counter);
    this.Linechart.data.datasets.forEach((dataset) => {
      // dataset.data = this.runs1;
    });
    for(let i = 0; i < 10; i++){
      this.runs1[i] = i + this.counter;
    }
    console.log(this.counter);
    this.Linechart.update();
    //this.display_comparison_chart();
  }

}