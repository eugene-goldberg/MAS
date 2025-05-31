# Attention Is All You Need

**Title**: Attention Is All You Need

**Primary Authors**: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin

**Publication Year**: 2017

**Authors with Affiliations**:
- Ashish Vaswani (Google Brain)
- Noam Shazeer (Google Brain) 
- Niki Parmar (Google Research)
- Jakob Uszkoreit (Google Research)
- Llion Jones (Google Research)
- Aidan N. Gomez (University of Toronto)
- Łukasz Kaiser (Google Brain)
- Illia Polosukhin (Google Research)

**Abstract**:
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.

**Summary**:
This seminal paper introduces the Transformer architecture, a revolutionary approach to sequence transduction that relies entirely on self-attention mechanisms, eliminating the need for recurrent or convolutional layers. The authors demonstrate that this architecture not only achieves state-of-the-art performance on machine translation tasks but also offers significant computational advantages through improved parallelization. The model's core innovation lies in its multi-head self-attention mechanism, which allows the model to attend to different positions simultaneously and capture various types of relationships in the input sequence. The Transformer's encoder-decoder structure, combined with positional encodings and layer normalization, enables it to process sequences more efficiently than previous architectures. The paper's experimental results on WMT translation benchmarks show substantial improvements over existing methods, while requiring less training time, marking a paradigm shift in how sequence-to-sequence models are designed.

**Key Topics/Keywords**:
- Transformer architecture
- Self-attention mechanism
- Multi-head attention
- Sequence transduction
- Machine translation
- Encoder-decoder models
- Positional encoding
- Parallelization
- Neural machine translation

**Key Innovations**:
• Introduced the Transformer architecture based solely on attention mechanisms, eliminating recurrence and convolutions
• Developed multi-head self-attention to allow models to jointly attend to information from different representation subspaces
• Demonstrated that attention-only models can outperform recurrent and convolutional models on translation tasks
• Achieved significant training time reduction through improved parallelization compared to sequential RNN processing
• Established new state-of-the-art results on WMT 2014 English-German and English-French translation benchmarks

**References Cited Within Seminal Paper**:
Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation by jointly learning to align and translate. ICLR, 2015.

Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E. Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.

Denny Britz, Anna Goldie, Minh-Thang Luong, and Quoc V. Le. Massive exploration of neural machine translation architectures. arXiv preprint arXiv:1703.03906, 2017.

Jianpeng Cheng, Li Dong, and Mirella Lapata. Long short-term memory-networks for machine reading. EMNLP, 2016.

Kyunghyun Cho, Bart van Merrienboer, Caglar Gulcehre, Dzmitry Bahdanau, Fethi Bougares, Holger Schwenk, and Yoshua Bengio. Learning phrase representations using rnn encoder-decoder for statistical machine translation. EMNLP, 2014.

Francois Chollet. Xception: Deep learning with depthwise separable convolutions. arXiv preprint arXiv:1610.02357, 2016.

Junyoung Chung, Caglar Gulcehre, Kyunghyun Cho, and Yoshua Bengio. Empirical evaluation of gated recurrent neural networks on sequence modeling. arXiv preprint arXiv:1412.3555, 2014.

Jonas Gehring, Michael Auli, David Grangier, Denis Yarats, and Yann N. Dauphin. Convolutional sequence to sequence learning. arXiv preprint arXiv:1705.03122, 2017.

Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. CVPR, 2016.

Sepp Hochreiter and Jurgen Schmidhuber. Long short-term memory. Neural Computation, 9(8):1735-1780, 1997.

Yoon Kim, Carl Denton, Luong Hoang, and Alexander M. Rush. Structured attention networks. ICLR, 2017.

Minh-Thang Luong, Hieu Pham, and Christopher D. Manning. Effective approaches to attention-based neural machine translation. EMNLP, 2015.

Ankur Parikh, Oscar Tackstrom, Dipanjan Das, and Jakob Uszkoreit. A decomposable attention model for natural language inference. EMNLP, 2016.