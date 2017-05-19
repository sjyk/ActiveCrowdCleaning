function error = eval_model_sum(pred_Y, Y)
error = (sum(pred_Y) - sum(Y))^2/(sum(Y))^2;